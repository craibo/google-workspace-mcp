import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from src.tools.drive_tools import (
    search_drive_by_content,
    search_within_file_content,
    _find_content_matches,
    _generate_search_snippets
)


class TestContentSearch:
    """Test cases for Google Drive content search functionality."""

    @pytest.mark.asyncio
    async def test_search_drive_by_content_basic(self):
        """Test basic content search functionality."""
        with patch('src.tools.drive_tools.get_credentials') as mock_creds, \
             patch('src.tools.drive_tools.build') as mock_build, \
             patch('src.tools.drive_tools._extract_file_content_for_search') as mock_extract:
            
            # Mock credentials and service
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Mock file list response
            mock_files = [
                {
                    "id": "file1",
                    "name": "test_doc.docx",
                    "mimeType": "application/vnd.google-apps.document",
                    "createdTime": "2023-01-01T00:00:00Z",
                    "modifiedTime": "2023-01-02T00:00:00Z",
                    "size": "1024",
                    "parents": ["folder1"]
                }
            ]
            
            mock_service.files().list().execute.return_value = {"files": mock_files}
            
            # Mock content extraction
            mock_extract.return_value = {
                "has_matches": True,
                "snippets": [{"text": "test content", "match_start": 0, "match_end": 4}],
                "match_count": 1
            }
            
            result = await search_drive_by_content("test")
            result_data = json.loads(result)
            
            assert "results" in result_data
            assert len(result_data["results"]) == 1
            assert result_data["results"][0]["name"] == "test_doc.docx"
            assert result_data["results"][0]["match_count"] == 1

    @pytest.mark.asyncio
    async def test_search_drive_by_content_empty_term(self):
        """Test search with empty search term."""
        result = await search_drive_by_content("")
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "cannot be empty" in result_data["error"]

    @pytest.mark.asyncio
    async def test_search_drive_by_content_with_folder_filter(self):
        """Test content search with folder filter."""
        with patch('src.tools.drive_tools.get_credentials') as mock_creds, \
             patch('src.tools.drive_tools.build') as mock_build, \
             patch('src.tools.drive_tools._extract_file_content_for_search') as mock_extract:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            mock_service.files().list().execute.return_value = {"files": []}
            mock_extract.return_value = {"has_matches": False, "snippets": [], "match_count": 0}
            
            result = await search_drive_by_content("test", folder_id="folder123")
            result_data = json.loads(result)
            
            # Verify the query was built with folder filter
            mock_service.files().list.assert_called()
            call_args = mock_service.files().list.call_args
            assert "'folder123' in parents" in call_args[1]['q']

    @pytest.mark.asyncio
    async def test_search_drive_by_content_with_regex(self):
        """Test content search with regex enabled."""
        with patch('src.tools.drive_tools.get_credentials') as mock_creds, \
             patch('src.tools.drive_tools.build') as mock_build, \
             patch('src.tools.drive_tools._extract_file_content_for_search') as mock_extract:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            mock_service.files().list().execute.return_value = {"files": []}
            mock_extract.return_value = {"has_matches": False, "snippets": [], "match_count": 0}
            
            result = await search_drive_by_content("test.*", use_regex=True)
            result_data = json.loads(result)
            
            assert "results" in result_data
            assert result_data["total_matches"] == 0

    @pytest.mark.asyncio
    async def test_search_within_file_content(self):
        """Test searching within a specific file."""
        with patch('src.tools.drive_tools.get_credentials') as mock_creds, \
             patch('src.tools.drive_tools.build') as mock_build, \
             patch('src.tools.drive_tools._extract_file_content_for_search') as mock_extract:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Mock file metadata
            mock_service.files().get().execute.return_value = {
                "id": "file123",
                "name": "test_file.pdf",
                "mimeType": "application/pdf",
                "createdTime": "2023-01-01T00:00:00Z",
                "modifiedTime": "2023-01-02T00:00:00Z",
                "size": "2048"
            }
            
            # Mock content extraction
            mock_extract.return_value = {
                "has_matches": True,
                "snippets": [{"text": "found test content", "match_start": 6, "match_end": 10}],
                "match_count": 1
            }
            
            result = await search_within_file_content("file123", "test")
            result_data = json.loads(result)
            
            assert result_data["file_id"] == "file123"
            assert result_data["file_name"] == "test_file.pdf"
            assert result_data["has_matches"] is True
            assert result_data["match_count"] == 1

    def test_find_content_matches_simple(self):
        """Test simple string matching."""
        content = "This is a test document with test content"
        matches = _find_content_matches(content, "test", case_sensitive=False, use_regex=False)
        
        assert len(matches) == 2
        assert matches[0] == (10, 14)  # First "test"
        assert matches[1] == (29, 33)  # Second "test" (corrected position)

    def test_find_content_matches_case_sensitive(self):
        """Test case-sensitive string matching."""
        content = "This is a Test document with test content"
        matches = _find_content_matches(content, "Test", case_sensitive=True, use_regex=False)
        
        assert len(matches) == 1
        assert matches[0] == (10, 14)  # Only "Test"

    def test_find_content_matches_regex(self):
        """Test regex pattern matching."""
        content = "test123 test456 test789"
        matches = _find_content_matches(content, r"test\d+", case_sensitive=False, use_regex=True)
        
        assert len(matches) == 3
        assert matches[0] == (0, 7)   # "test123"
        assert matches[1] == (8, 15)  # "test456"
        assert matches[2] == (16, 23) # "test789"

    def test_find_content_matches_invalid_regex(self):
        """Test fallback when regex is invalid."""
        content = "test content"
        matches = _find_content_matches(content, "[invalid", case_sensitive=False, use_regex=True)
        
        # Invalid regex should return no matches (not fall back to string search)
        assert len(matches) == 0

    def test_generate_search_snippets(self):
        """Test snippet generation around matches."""
        content = "This is a long document with some test content that contains multiple test words"
        matches = [(23, 27), (58, 62)]  # Two "test" matches
        
        snippets = _generate_search_snippets(content, matches, snippet_length=20)
        
        assert len(snippets) == 2
        # Check that snippets contain parts of the content
        snippet_texts = [s["text"] for s in snippets]
        assert "g document with some tes" in snippet_texts[0]
        assert "hat contains multiple te" in snippet_texts[1]
        assert snippets[0]["match_start"] < snippets[0]["match_end"]

    def test_generate_search_snippets_edge_cases(self):
        """Test snippet generation with edge cases."""
        content = "short"
        matches = [(0, 5)]  # Match entire content
        
        snippets = _generate_search_snippets(content, matches, snippet_length=10)
        
        assert len(snippets) == 1
        assert snippets[0]["text"] == "short"
        assert snippets[0]["match_start"] == 0
        assert snippets[0]["match_end"] == 5

    @pytest.mark.asyncio
    async def test_search_drive_by_content_error_handling(self):
        """Test error handling in content search."""
        with patch('src.tools.drive_tools.get_credentials') as mock_creds, \
             patch('src.tools.drive_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Mock API error
            from googleapiclient.errors import HttpError
            mock_service.files().list().execute.side_effect = HttpError(
                resp=Mock(status=500), content=b"Internal Server Error"
            )
            
            result = await search_drive_by_content("test")
            result_data = json.loads(result)
            
            assert "error" in result_data
            assert "An error occurred" in result_data["error"]

    @pytest.mark.asyncio
    async def test_search_within_file_content_error_handling(self):
        """Test error handling in single file search."""
        with patch('src.tools.drive_tools.get_credentials') as mock_creds, \
             patch('src.tools.drive_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Mock API error
            from googleapiclient.errors import HttpError
            mock_service.files().get().execute.side_effect = HttpError(
                resp=Mock(status=404), content=b"File not found"
            )
            
            result = await search_within_file_content("invalid_id", "test")
            result_data = json.loads(result)
            
            assert "error" in result_data
            assert "An error occurred" in result_data["error"]
