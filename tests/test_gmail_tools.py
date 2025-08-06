import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from src.tools.gmail_tools import (
    search_gmail,
    list_gmail_labels,
    search_gmail_labels,
    get_gmail_label_details,
    search_gmail_by_label,
    get_gmail_message_details
)


class TestGmailLabels:
    """Test cases for Gmail label functionality."""

    @pytest.mark.asyncio
    async def test_list_gmail_labels(self):
        """Test listing all Gmail labels."""
        with patch('src.tools.gmail_tools.get_credentials') as mock_creds, \
             patch('src.tools.gmail_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Mock labels response
            mock_labels = [
                {
                    "id": "INBOX",
                    "name": "INBOX",
                    "type": "system",
                    "messageListVisibility": "show",
                    "labelListVisibility": "labelShow",
                    "messagesTotal": 150,
                    "messagesUnread": 5
                },
                {
                    "id": "Label_123",
                    "name": "Work",
                    "type": "user",
                    "messageListVisibility": "show",
                    "labelListVisibility": "labelShow",
                    "messagesTotal": 25,
                    "messagesUnread": 2
                }
            ]
            
            mock_service.users().labels().list().execute.return_value = {"labels": mock_labels}
            
            result = await list_gmail_labels()
            result_data = json.loads(result)
            
            assert "labels" in result_data
            assert len(result_data["labels"]) == 2
            assert result_data["total_labels"] == 2
            assert result_data["labels"][0]["id"] == "INBOX"
            assert result_data["labels"][1]["name"] == "Work"

    @pytest.mark.asyncio
    async def test_search_gmail_labels_with_query(self):
        """Test searching labels with a query."""
        with patch('src.tools.gmail_tools.get_credentials') as mock_creds, \
             patch('src.tools.gmail_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Mock all labels
            mock_labels = [
                {"id": "Label_1", "name": "Work", "type": "user"},
                {"id": "Label_2", "name": "Personal", "type": "user"},
                {"id": "Label_3", "name": "Work Projects", "type": "user"}
            ]
            
            mock_service.users().labels().list().execute.return_value = {"labels": mock_labels}
            
            result = await search_gmail_labels("work")
            result_data = json.loads(result)
            
            assert "labels" in result_data
            assert len(result_data["labels"]) == 2  # "Work" and "Work Projects"
            assert result_data["query"] == "work"
            assert all("work" in label["name"].lower() for label in result_data["labels"])

    @pytest.mark.asyncio
    async def test_search_gmail_labels_empty_query(self):
        """Test searching labels with empty query returns all labels."""
        with patch('src.tools.gmail_tools.get_credentials') as mock_creds, \
             patch('src.tools.gmail_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            mock_labels = [
                {"id": "Label_1", "name": "Work", "type": "user"},
                {"id": "Label_2", "name": "Personal", "type": "user"}
            ]
            
            mock_service.users().labels().list().execute.return_value = {"labels": mock_labels}
            
            result = await search_gmail_labels("")
            result_data = json.loads(result)
            
            assert len(result_data["labels"]) == 2
            assert result_data["query"] == ""

    @pytest.mark.asyncio
    async def test_get_gmail_label_details(self):
        """Test getting details for a specific label."""
        with patch('src.tools.gmail_tools.get_credentials') as mock_creds, \
             patch('src.tools.gmail_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            mock_label = {
                "id": "Label_123",
                "name": "Work",
                "type": "user",
                "messageListVisibility": "show",
                "labelListVisibility": "labelShow",
                "messagesTotal": 25,
                "messagesUnread": 2,
                "threadsTotal": 15,
                "threadsUnread": 1
            }
            
            mock_service.users().labels().get().execute.return_value = mock_label
            
            result = await get_gmail_label_details("Label_123")
            result_data = json.loads(result)
            
            assert result_data["id"] == "Label_123"
            assert result_data["name"] == "Work"
            assert result_data["messagesTotal"] == 25
            assert result_data["messagesUnread"] == 2
            assert result_data["threadsTotal"] == 15
            assert result_data["threadsUnread"] == 1

    @pytest.mark.asyncio
    async def test_search_gmail_by_label(self):
        """Test searching messages within a specific label."""
        with patch('src.tools.gmail_tools.get_credentials') as mock_creds, \
             patch('src.tools.gmail_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Mock messages in label
            mock_messages = [
                {"id": "msg1"},
                {"id": "msg2"}
            ]
            
            mock_service.users().messages().list().execute.return_value = {"messages": mock_messages}
            
            # Mock individual message details
            def mock_get_message(userId, id):
                mock_msg = Mock()
                if id == "msg1":
                    mock_msg.execute.return_value = {
                        "id": "msg1",
                        "payload": {
                            "headers": [
                                {"name": "Subject", "value": "Test Email 1"},
                                {"name": "From", "value": "sender1@example.com"},
                                {"name": "Date", "value": "2023-01-01"}
                            ]
                        },
                        "labelIds": ["Label_123", "INBOX"],
                        "snippet": "This is a test email"
                    }
                else:
                    mock_msg.execute.return_value = {
                        "id": "msg2",
                        "payload": {
                            "headers": [
                                {"name": "Subject", "value": "Test Email 2"},
                                {"name": "From", "value": "sender2@example.com"},
                                {"name": "Date", "value": "2023-01-02"}
                            ]
                        },
                        "labelIds": ["Label_123"],
                        "snippet": "Another test email"
                    }
                return mock_msg
            
            mock_service.users().messages().get.side_effect = mock_get_message
            
            result = await search_gmail_by_label("Label_123", "test")
            result_data = json.loads(result)
            
            assert "messages" in result_data
            assert len(result_data["messages"]) == 2
            assert result_data["label_id"] == "Label_123"
            assert result_data["query"] == "test"
            assert result_data["total_results"] == 2

    @pytest.mark.asyncio
    async def test_search_gmail_with_label_filter(self):
        """Test searching Gmail with label filter."""
        with patch('src.tools.gmail_tools.get_credentials') as mock_creds, \
             patch('src.tools.gmail_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Mock messages
            mock_messages = [{"id": "msg1"}]
            mock_service.users().messages().list().execute.return_value = {"messages": mock_messages}
            
            # Mock message details
            mock_service.users().messages().get().execute.return_value = {
                "id": "msg1",
                "payload": {
                    "headers": [
                        {"name": "Subject", "value": "Test Email"},
                        {"name": "From", "value": "sender@example.com"},
                        {"name": "Date", "value": "2023-01-01"}
                    ]
                },
                "labelIds": ["INBOX", "Label_123"],
                "snippet": "Test email content"
            }
            
            result = await search_gmail("test", label_ids=["INBOX"])
            result_data = json.loads(result)
            
            assert "messages" in result_data
            assert len(result_data["messages"]) == 1
            assert result_data["label_ids"] == ["INBOX"]
            assert result_data["query"] == "test"

    @pytest.mark.asyncio
    async def test_search_gmail_without_label_filter(self):
        """Test searching Gmail without label filter."""
        with patch('src.tools.gmail_tools.get_credentials') as mock_creds, \
             patch('src.tools.gmail_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            mock_messages = [{"id": "msg1"}]
            mock_service.users().messages().list().execute.return_value = {"messages": mock_messages}
            
            mock_service.users().messages().get().execute.return_value = {
                "id": "msg1",
                "payload": {
                    "headers": [
                        {"name": "Subject", "value": "Test Email"},
                        {"name": "From", "value": "sender@example.com"},
                        {"name": "Date", "value": "2023-01-01"}
                    ]
                },
                "labelIds": ["INBOX"],
                "snippet": "Test email content"
            }
            
            result = await search_gmail("test")
            result_data = json.loads(result)
            
            assert "messages" in result_data
            assert result_data["label_ids"] is None
            assert result_data["query"] == "test"

    @pytest.mark.asyncio
    async def test_get_gmail_message_details_with_labels(self):
        """Test getting message details includes labels."""
        with patch('src.tools.gmail_tools.get_credentials') as mock_creds, \
             patch('src.tools.gmail_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            mock_service.users().messages().get().execute.return_value = {
                "id": "msg1",
                "payload": {
                    "headers": [
                        {"name": "Subject", "value": "Test Email"},
                        {"name": "From", "value": "sender@example.com"},
                        {"name": "To", "value": "recipient@example.com"},
                        {"name": "Date", "value": "2023-01-01"}
                    ],
                    "body": {
                        "data": "VGVzdCBib2R5IGNvbnRlbnQ="  # base64 encoded "Test body content"
                    }
                },
                "labelIds": ["INBOX", "Label_123"],
                "snippet": "Test email snippet"
            }
            
            result = await get_gmail_message_details("msg1")
            result_data = json.loads(result)
            
            assert result_data["id"] == "msg1"
            assert result_data["subject"] == "Test Email"
            assert result_data["from"] == "sender@example.com"
            assert result_data["labels"] == ["INBOX", "Label_123"]
            assert result_data["snippet"] == "Test email snippet"

    @pytest.mark.asyncio
    async def test_gmail_error_handling(self):
        """Test error handling in Gmail operations."""
        with patch('src.tools.gmail_tools.get_credentials') as mock_creds, \
             patch('src.tools.gmail_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            # Mock API error
            from googleapiclient.errors import HttpError
            mock_service.users().labels().list().execute.side_effect = HttpError(
                resp=Mock(status=500), content=b"Internal Server Error"
            )
            
            result = await list_gmail_labels()
            result_data = json.loads(result)
            
            assert "error" in result_data
            assert "An error occurred" in result_data["error"]

    @pytest.mark.asyncio
    async def test_search_gmail_by_label_empty_results(self):
        """Test searching by label with no results."""
        with patch('src.tools.gmail_tools.get_credentials') as mock_creds, \
             patch('src.tools.gmail_tools.build') as mock_build:
            
            mock_creds.return_value = Mock()
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            mock_service.users().messages().list().execute.return_value = {"messages": []}
            
            result = await search_gmail_by_label("Label_123", "nonexistent")
            result_data = json.loads(result)
            
            assert "messages" in result_data
            assert len(result_data["messages"]) == 0
            assert result_data["total_results"] == 0
            assert result_data["label_id"] == "Label_123"
            assert result_data["query"] == "nonexistent"
