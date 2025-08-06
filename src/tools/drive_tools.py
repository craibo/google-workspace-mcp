import json
import asyncio
import re
import io
import logging
from typing import List, Dict, Optional, Tuple
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import PyPDF2

from src.auth import get_credentials
from src.mcp_instance import mcp
from src.config import get_supported_content_search_types, get_max_content_search_results, get_content_search_snippet_length

logger = logging.getLogger(__name__)

@mcp.tool()
async def search_drive(query: str) -> str:
    """
    Searches for files in Google Drive matching the query.

    Args:
        query: The search string.

    Returns:
        A JSON string representing a list of files.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "drive", "v3", credentials=creds)
        
        def _search():
            return service.files().list(
                q=query, pageSize=10, fields="files(id, name, mimeType)"
            ).execute()

        results = await asyncio.to_thread(_search)
        items = results.get("files", [])
        return json.dumps(items)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def get_drive_file_details(file_id: str) -> str:
    """
    Fetches the metadata and content of a specific file by its ID.
    For Google Docs/Sheets/Slides, it exports the content as plain text.

    Args:
        file_id: The unique ID of the file.

    Returns:
        A JSON string with file details.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "drive", "v3", credentials=creds)

        def _get_metadata():
            return service.files().get(fileId=file_id, fields="*").execute()

        file_metadata = await asyncio.to_thread(_get_metadata)
        mime_type = file_metadata.get("mimeType")
        content = None

        if "google-apps" in mime_type:
            def _export():
                request = service.files().export_media(fileId=file_id, mimeType="text/plain")
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                return fh.getvalue().decode()
            
            content = await asyncio.to_thread(_export)

        file_details = {
            "id": file_metadata.get("id"),
            "name": file_metadata.get("name"),
            "mimeType": mime_type,
            "createdTime": file_metadata.get("createdTime"),
            "modifiedTime": file_metadata.get("modifiedTime"),
            "content": content,
        }
        return json.dumps(file_details)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def search_drive_by_content(
    search_term: str,
    folder_id: Optional[str] = None,
    file_types: Optional[List[str]] = None,
    case_sensitive: bool = False,
    use_regex: bool = False,
    max_results: Optional[int] = None
) -> str:
    """
    Searches for files in Google Drive containing the specified text content.
    
    Args:
        search_term: The text to search for in file content
        folder_id: Optional folder ID to limit search scope
        file_types: Optional list of MIME types to search (defaults to supported types)
        case_sensitive: Whether to perform case-sensitive search
        use_regex: Whether to treat search_term as a regex pattern
        max_results: Maximum number of results to return (defaults to config)
        
    Returns:
        A JSON string with search results including file metadata and content snippets
    """
    if not search_term.strip():
        return json.dumps({"error": "Search term cannot be empty"})
    
    if max_results is None:
        max_results = get_max_content_search_results()
    
    if file_types is None:
        file_types = get_supported_content_search_types()
    
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "drive", "v3", credentials=creds)
        
        # Build search query
        query_parts = []
        
        # Add full-text search
        if use_regex:
            # For regex, we'll need to search more broadly and filter later
            query_parts.append(f"fullText contains '{search_term}'")
        else:
            if case_sensitive:
                query_parts.append(f"fullText contains '{search_term}'")
            else:
                query_parts.append(f"fullText contains '{search_term.lower()}'")
        
        # Add file type filter
        if file_types:
            mime_type_query = " or ".join([f"mimeType = '{mime_type}'" for mime_type in file_types])
            query_parts.append(f"({mime_type_query})")
        
        # Add folder filter
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        
        query = " and ".join(query_parts)
        
        def _search():
            return service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, createdTime, modifiedTime, size, parents)"
            ).execute()
        
        results = await asyncio.to_thread(_search)
        files = results.get("files", [])
        
        # Process results and extract content snippets
        search_results = []
        for file in files:
            content_info = await _extract_file_content_for_search(
                service, file["id"], file["mimeType"], search_term, 
                case_sensitive, use_regex
            )
            
            if content_info["has_matches"]:
                search_results.append({
                    "id": file["id"],
                    "name": file["name"],
                    "mimeType": file["mimeType"],
                    "createdTime": file.get("createdTime"),
                    "modifiedTime": file.get("modifiedTime"),
                    "size": file.get("size"),
                    "parents": file.get("parents", []),
                    "snippets": content_info["snippets"],
                    "match_count": content_info["match_count"]
                })
        
        return json.dumps({
            "results": search_results,
            "total_matches": len(search_results),
            "search_term": search_term,
            "query": query
        })
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

async def _extract_file_content_for_search(
    service, file_id: str, mime_type: str, search_term: str, 
    case_sensitive: bool, use_regex: bool
) -> Dict:
    """
    Extracts content from a file and searches for matches.
    
    Returns:
        Dict with has_matches, snippets, and match_count
    """
    try:
        content = None
        
        # Handle Google Apps files
        if "google-apps" in mime_type:
            content = await _extract_google_apps_content(service, file_id)
        
        # Handle PDF files
        elif mime_type == "application/pdf":
            content = await _extract_pdf_content(service, file_id)
        
        # Handle text files
        elif mime_type.startswith("text/"):
            content = await _extract_text_content(service, file_id)
        
        if not content:
            return {"has_matches": False, "snippets": [], "match_count": 0}
        
        # Search for matches
        matches = _find_content_matches(content, search_term, case_sensitive, use_regex)
        
        if not matches:
            return {"has_matches": False, "snippets": [], "match_count": 0}
        
        # Generate snippets
        snippets = _generate_search_snippets(content, matches, get_content_search_snippet_length())
        
        return {
            "has_matches": True,
            "snippets": snippets,
            "match_count": len(matches)
        }
        
    except Exception as e:
        logger.error(f"Error extracting content from file {file_id}: {e}")
        return {"has_matches": False, "snippets": [], "match_count": 0}

async def _extract_google_apps_content(service, file_id: str) -> Optional[str]:
    """Extract content from Google Apps files."""
    try:
        def _export():
            request = service.files().export_media(fileId=file_id, mimeType="text/plain")
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            return fh.getvalue().decode('utf-8')
        
        return await asyncio.to_thread(_export)
    except Exception as e:
        logger.error(f"Error extracting Google Apps content: {e}")
        return None

async def _extract_pdf_content(service, file_id: str) -> Optional[str]:
    """Extract text content from PDF files."""
    try:
        def _download_and_extract():
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            
            # Extract text from PDF
            fh.seek(0)
            pdf_reader = PyPDF2.PdfReader(fh)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        return await asyncio.to_thread(_download_and_extract)
    except Exception as e:
        logger.error(f"Error extracting PDF content: {e}")
        return None

async def _extract_text_content(service, file_id: str) -> Optional[str]:
    """Extract content from text files."""
    try:
        def _download():
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            return fh.getvalue().decode('utf-8')
        
        return await asyncio.to_thread(_download)
    except Exception as e:
        logger.error(f"Error extracting text content: {e}")
        return None

def _find_content_matches(content: str, search_term: str, case_sensitive: bool, use_regex: bool) -> List[Tuple[int, int]]:
    """
    Find all matches of search_term in content.
    
    Returns:
        List of (start_pos, end_pos) tuples
    """
    matches = []
    
    if use_regex:
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(search_term, flags)
            for match in pattern.finditer(content):
                matches.append((match.start(), match.end()))
        except re.error:
            # If regex is invalid, fall back to simple string search
            return _find_content_matches(content, search_term, case_sensitive, False)
    else:
        search_text = search_term if case_sensitive else search_term.lower()
        content_text = content if case_sensitive else content.lower()
        
        start = 0
        while True:
            pos = content_text.find(search_text, start)
            if pos == -1:
                break
            matches.append((pos, pos + len(search_term)))
            start = pos + 1
    
    return matches

def _generate_search_snippets(content: str, matches: List[Tuple[int, int]], snippet_length: int) -> List[Dict]:
    """
    Generate snippets around matches for display.
    
    Returns:
        List of snippet dictionaries with text and match positions
    """
    snippets = []
    half_length = snippet_length // 2
    
    for start, end in matches:
        # Calculate snippet boundaries
        snippet_start = max(0, start - half_length)
        snippet_end = min(len(content), end + half_length)
        
        # Extract snippet text
        snippet_text = content[snippet_start:snippet_end]
        
        # Adjust match positions relative to snippet
        match_start = start - snippet_start
        match_end = end - snippet_start
        
        snippets.append({
            "text": snippet_text,
            "match_start": match_start,
            "match_end": match_end,
            "original_start": start,
            "original_end": end
        })
    
    return snippets

@mcp.tool()
async def search_within_file_content(file_id: str, search_term: str, case_sensitive: bool = False, use_regex: bool = False) -> str:
    """
    Search for specific content within a single file.
    
    Args:
        file_id: The ID of the file to search
        search_term: The text to search for
        case_sensitive: Whether to perform case-sensitive search
        use_regex: Whether to treat search_term as a regex pattern
        
    Returns:
        JSON string with search results for the specific file
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "drive", "v3", credentials=creds)
        
        # Get file metadata
        def _get_metadata():
            return service.files().get(fileId=file_id, fields="id, name, mimeType, createdTime, modifiedTime, size").execute()
        
        file_metadata = await asyncio.to_thread(_get_metadata)
        
        # Extract and search content
        content_info = await _extract_file_content_for_search(
            service, file_id, file_metadata["mimeType"], search_term, 
            case_sensitive, use_regex
        )
        
        result = {
            "file_id": file_id,
            "file_name": file_metadata["name"],
            "mime_type": file_metadata["mimeType"],
            "created_time": file_metadata.get("createdTime"),
            "modified_time": file_metadata.get("modifiedTime"),
            "size": file_metadata.get("size"),
            "has_matches": content_info["has_matches"],
            "match_count": content_info["match_count"],
            "snippets": content_info["snippets"]
        }
        
        return json.dumps(result)
        
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
