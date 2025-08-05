import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from src.tools.drive_tools import search_drive, get_drive_file_details

@pytest.mark.asyncio
@patch("src.tools.drive_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.drive_tools.build", new_callable=MagicMock)
async def test_search_drive(mock_build, mock_get_credentials):
    """
    Tests the search_drive function.
    """
    # Mock the Google Drive API response
    mock_service = MagicMock()
    mock_files = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "files": [{"id": "123", "name": "test.txt", "mimeType": "text/plain"}]
    }
    mock_files.list.return_value = mock_list
    mock_service.files.return_value = mock_files
    mock_build.return_value = mock_service

    # Call the function
    result = await search_drive("test query")

    # Assert the result
    assert json.loads(result) == [{"id": "123", "name": "test.txt", "mimeType": "text/plain"}]

@pytest.mark.asyncio
@patch("src.tools.drive_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.drive_tools.build", new_callable=MagicMock)
async def test_get_drive_file_details(mock_build, mock_get_credentials):
    """
    Tests the get_drive_file_details function.
    """
    # Mock the Google Drive API response
    mock_service = MagicMock()
    mock_files = MagicMock()
    mock_get = MagicMock()
    mock_get.execute.return_value = {
        "id": "123",
        "name": "test.txt",
        "mimeType": "text/plain",
        "createdTime": "2023-01-01T00:00:00Z",
        "modifiedTime": "2023-01-01T00:00:00Z",
    }
    mock_files.get.return_value = mock_get
    mock_service.files.return_value = mock_files
    mock_build.return_value = mock_service

    # Call the function
    result = await get_drive_file_details("123")

    # Assert the result
    expected = {
        "id": "123",
        "name": "test.txt",
        "mimeType": "text/plain",
        "createdTime": "2023-01-01T00:00:00Z",
        "modifiedTime": "2023-01-01T00:00:00Z",
        "content": None,
    }
    assert json.loads(result) == expected
