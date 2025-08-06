import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

# Test Option 1: Smart Default with Optional Override
from src.tools.calendar_tools import list_calendar_events, search_calendar_events, get_calendar_event_details

# Option 1 Tests
@pytest.mark.asyncio
@patch("src.tools.calendar_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.calendar_tools.build", new_callable=MagicMock)
@patch("src.tools.calendar_tools.get_default_calendar_ids", return_value=["primary"])
async def test_list_calendar_events_with_defaults(mock_get_defaults, mock_build, mock_get_credentials):
    """
    Tests Option 1: list_calendar_events with default calendar IDs.
    """
    # Mock the Calendar API response
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "items": [
            {
                "id": "event1",
                "summary": "Team Meeting",
                "start": {"dateTime": "2023-01-01T10:00:00+00:00"},
                "end": {"dateTime": "2023-01-01T11:00:00+00:00"}
            }
        ]
    }
    mock_events.list.return_value = mock_list
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function without calendar_ids (should use defaults)
    result = await list_calendar_events(
        start_time="2023-01-01T00:00:00Z",
        end_time="2023-01-02T00:00:00Z"
    )

    # Assert that get_default_calendar_ids was called
    mock_get_defaults.assert_called_once()
    
    # Assert the result
    expected = [
        {
            "id": "event1",
            "summary": "Team Meeting",
            "start": {"dateTime": "2023-01-01T10:00:00+00:00"},
            "end": {"dateTime": "2023-01-01T11:00:00+00:00"},
            "calendarId": "primary"
        }
    ]
    assert json.loads(result) == expected

@pytest.mark.asyncio
@patch("src.tools.calendar_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.calendar_tools.build", new_callable=MagicMock)
async def test_list_calendar_events_with_specific_calendars(mock_build, mock_get_credentials):
    """
    Tests Option 1: list_calendar_events with specific calendar IDs.
    """
    # Mock the Calendar API response
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "items": [
            {
                "id": "event2",
                "summary": "Work Meeting",
                "start": {"dateTime": "2023-01-01T14:00:00+00:00"},
                "end": {"dateTime": "2023-01-01T15:00:00+00:00"}
            }
        ]
    }
    mock_events.list.return_value = mock_list
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function with specific calendar_ids
    result = await list_calendar_events(
        calendar_ids=["work@company.com"],
        start_time="2023-01-01T00:00:00Z",
        end_time="2023-01-02T00:00:00Z"
    )

    # Assert the result
    expected = [
        {
            "id": "event2",
            "summary": "Work Meeting",
            "start": {"dateTime": "2023-01-01T14:00:00+00:00"},
            "end": {"dateTime": "2023-01-01T15:00:00+00:00"},
            "calendarId": "work@company.com"
        }
    ]
    assert json.loads(result) == expected

@pytest.mark.asyncio
@patch("src.tools.calendar_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.calendar_tools.build", new_callable=MagicMock)
@patch("src.tools.calendar_tools.get_default_calendar_ids", return_value=["primary"])
async def test_get_calendar_event_details_with_default(mock_get_defaults, mock_build, mock_get_credentials):
    """
    Tests Option 1: get_calendar_event_details with default calendar.
    """
    # Mock the Calendar API response
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_get = MagicMock()
    mock_get.execute.return_value = {
        "id": "event1",
        "summary": "Team Meeting",
        "description": "Weekly team sync"
    }
    mock_events.get.return_value = mock_get
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function without calendar_id (should use default)
    result = await get_calendar_event_details("event1")

    # Assert that get_default_calendar_ids was called
    mock_get_defaults.assert_called_once()
    
    # Assert the result
    expected = {
        "id": "event1",
        "summary": "Team Meeting",
        "description": "Weekly team sync"
    }
    assert json.loads(result) == expected

@pytest.mark.asyncio
@patch("src.tools.calendar_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.calendar_tools.build", new_callable=MagicMock)
async def test_get_calendar_event_details_with_specific_calendar(mock_build, mock_get_credentials):
    """
    Tests Option 1: get_calendar_event_details with specific calendar ID.
    """
    # Mock the Calendar API response
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_get = MagicMock()
    mock_get.execute.return_value = {
        "id": "event2",
        "summary": "Work Meeting",
        "description": "Work calendar event"
    }
    mock_events.get.return_value = mock_get
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function with specific calendar_id
    result = await get_calendar_event_details("event2", "work@company.com")

    # Assert the result
    expected = {
        "id": "event2",
        "summary": "Work Meeting",
        "description": "Work calendar event"
    }
    assert json.loads(result) == expected

@pytest.mark.asyncio
@patch("src.tools.calendar_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.calendar_tools.build", new_callable=MagicMock)
async def test_search_calendar_events_with_defaults(mock_build, mock_get_credentials):
    """
    Tests Option 1: search_calendar_events with default calendar IDs.
    """
    # Mock the Calendar API response
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "items": [
            {
                "id": "event3",
                "summary": "Project Review",
                "start": {"dateTime": "2023-01-01T16:00:00+00:00"},
                "end": {"dateTime": "2023-01-01T17:00:00+00:00"}
            }
        ]
    }
    mock_events.list.return_value = mock_list
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function without calendar_ids (should use defaults)
    result = await search_calendar_events(
        query="Project",
        start_time="2023-01-01T00:00:00Z",
        end_time="2023-01-02T00:00:00Z"
    )

    # Assert the result
    expected = [
        {
            "id": "event3",
            "summary": "Project Review",
            "start": {"dateTime": "2023-01-01T16:00:00+00:00"},
            "end": {"dateTime": "2023-01-01T17:00:00+00:00"},
            "calendarId": "primary"
        }
    ]
    assert json.loads(result) == expected 