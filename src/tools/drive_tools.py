import json
import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import io

from src.auth import get_credentials
from src.mcp_instance import mcp

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
