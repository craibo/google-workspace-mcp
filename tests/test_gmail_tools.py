import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import base64

from src.tools.gmail_tools import search_gmail, get_gmail_message_details

@pytest.mark.asyncio
@patch("src.tools.gmail_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.gmail_tools.build", new_callable=MagicMock)
async def test_search_gmail(mock_build, mock_get_credentials):
    """
    Tests the search_gmail function.
    """
    # Mock the Gmail API response
    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_messages = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {"messages": [{"id": "123"}]}
    mock_messages.list.return_value = mock_list
    
    mock_get = MagicMock()
    mock_get.execute.return_value = {
        "id": "123",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test Subject"},
                {"name": "From", "value": "test@example.com"},
                {"name": "Date", "value": "2023-01-01T00:00:00Z"},
            ]
        }
    }
    mock_messages.get.return_value = mock_get
    mock_users.messages.return_value = mock_messages
    mock_service.users.return_value = mock_users
    mock_build.return_value = mock_service

    # Call the function
    result = await search_gmail("test query")

    # Assert the result
    expected = [{
        "id": "123",
        "subject": "Test Subject",
        "from": "test@example.com",
        "date": "2023-01-01T00:00:00Z",
    }]
    assert json.loads(result) == expected

@pytest.mark.asyncio
@patch("src.tools.gmail_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.gmail_tools.build", new_callable=MagicMock)
async def test_get_gmail_message_details(mock_build, mock_get_credentials):
    """
    Tests the get_gmail_message_details function.
    """
    # Mock the Gmail API response
    mock_service = MagicMock()
    mock_users = MagicMock()
    mock_messages = MagicMock()
    mock_get = MagicMock()
    
    body_text = "Hello, this is a test email."
    encoded_body = base64.urlsafe_b64encode(body_text.encode("utf-8")).decode("utf-8")

    mock_get.execute.return_value = {
        "id": "123",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test Subject"},
                {"name": "From", "value": "test@example.com"},
                {"name": "To", "value": "recipient@example.com"},
                {"name": "Date", "value": "2023-01-01T00:00:00Z"},
            ],
            "body": {"data": encoded_body}
        }
    }
    mock_messages.get.return_value = mock_get
    mock_users.messages.return_value = mock_messages
    mock_service.users.return_value = mock_users
    mock_build.return_value = mock_service

    # Call the function
    result = await get_gmail_message_details("123")

    # Assert the result
    expected = {
        "id": "123",
        "subject": "Test Subject",
        "from": "test@example.com",
        "to": "recipient@example.com",
        "date": "2023-01-01T00:00:00Z",
        "body": body_text,
    }
    assert json.loads(result) == expected
