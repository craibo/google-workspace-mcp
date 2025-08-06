import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

from src.tools.calendar_tools import list_calendars, list_calendar_events, search_calendar_events, get_calendar_event_details

@pytest.mark.asyncio
@patch("src.tools.calendar_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.calendar_tools.build", new_callable=MagicMock)
async def test_list_calendars(mock_build, mock_get_credentials):
    """
    Tests the list_calendars function.
    """
    # Mock the Calendar API response
    mock_service = MagicMock()
    mock_calendar_list = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "items": [
            {
                "id": "primary",
                "summary": "Your Name",
                "description": "Primary calendar",
                "accessRole": "owner",
                "primary": True
            },
            {
                "id": "work@company.com",
                "summary": "Work Calendar",
                "description": "Company work calendar",
                "accessRole": "reader",
                "primary": False
            }
        ]
    }
    mock_calendar_list.list.return_value = mock_list
    mock_service.calendarList.return_value = mock_calendar_list
    mock_build.return_value = mock_service

    # Call the function
    result = await list_calendars()

    # Assert the result
    expected = [
        {
            "id": "primary",
            "summary": "Your Name",
            "description": "Primary calendar",
            "accessRole": "owner",
            "primary": True
        },
        {
            "id": "work@company.com",
            "summary": "Work Calendar",
            "description": "Company work calendar",
            "accessRole": "reader",
            "primary": False
        }
    ]
    assert json.loads(result) == expected

@pytest.mark.asyncio
@patch("src.tools.calendar_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.calendar_tools.build", new_callable=MagicMock)
async def test_list_calendar_events(mock_build, mock_get_credentials):
    """
    Tests the list_calendar_events function.
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

    # Call the function
    result = await list_calendar_events(
        calendar_ids=["primary"],
        start_time="2023-01-01T00:00:00Z",
        end_time="2023-01-02T00:00:00Z"
    )

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
async def test_list_calendar_events_with_query(mock_build, mock_get_credentials):
    """
    Tests the list_calendar_events function with query parameter.
    """
    # Mock the Calendar API response
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "items": [
            {
                "id": "event2",
                "summary": "Project Review",
                "start": {"dateTime": "2023-01-01T14:00:00+00:00"},
                "end": {"dateTime": "2023-01-01T15:00:00+00:00"}
            }
        ]
    }
    mock_events.list.return_value = mock_list
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function with query
    result = await list_calendar_events(
        calendar_ids=["primary"],
        start_time="2023-01-01T00:00:00Z",
        end_time="2023-01-02T00:00:00Z",
        query="Project"
    )

    # Assert the result
    expected = [
        {
            "id": "event2",
            "summary": "Project Review",
            "start": {"dateTime": "2023-01-01T14:00:00+00:00"},
            "end": {"dateTime": "2023-01-01T15:00:00+00:00"},
            "calendarId": "primary"
        }
    ]
    assert json.loads(result) == expected

@pytest.mark.asyncio
@patch("src.tools.calendar_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.calendar_tools.build", new_callable=MagicMock)
async def test_search_calendar_events(mock_build, mock_get_credentials):
    """
    Tests the search_calendar_events function.
    """
    # Mock the Calendar API response
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        "items": [
            {
                "id": "event3",
                "summary": "Client Meeting",
                "start": {"dateTime": "2023-01-01T16:00:00+00:00"},
                "end": {"dateTime": "2023-01-01T17:00:00+00:00"}
            }
        ]
    }
    mock_events.list.return_value = mock_list
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function
    result = await search_calendar_events(
        calendar_ids=["primary"],
        query="Client",
        start_time="2023-01-01T00:00:00Z",
        end_time="2023-01-02T00:00:00Z"
    )

    # Assert the result
    expected = [
        {
            "id": "event3",
            "summary": "Client Meeting",
            "start": {"dateTime": "2023-01-01T16:00:00+00:00"},
            "end": {"dateTime": "2023-01-01T17:00:00+00:00"},
            "calendarId": "primary"
        }
    ]
    assert json.loads(result) == expected

@pytest.mark.asyncio
@patch("src.tools.calendar_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.calendar_tools.build", new_callable=MagicMock)
async def test_get_calendar_event_details(mock_build, mock_get_credentials):
    """
    Tests the get_calendar_event_details function.
    """
    # Mock the Calendar API response
    mock_service = MagicMock()
    mock_events = MagicMock()
    mock_get = MagicMock()
    mock_get.execute.return_value = {
        "id": "event1",
        "summary": "Team Meeting",
        "description": "Weekly team sync",
        "start": {"dateTime": "2023-01-01T10:00:00+00:00"},
        "end": {"dateTime": "2023-01-01T11:00:00+00:00"},
        "attendees": [
            {"email": "john@example.com", "responseStatus": "accepted"}
        ]
    }
    mock_events.get.return_value = mock_get
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function
    result = await get_calendar_event_details("primary", "event1")

    # Assert the result
    expected = {
        "id": "event1",
        "summary": "Team Meeting",
        "description": "Weekly team sync",
        "start": {"dateTime": "2023-01-01T10:00:00+00:00"},
        "end": {"dateTime": "2023-01-01T11:00:00+00:00"},
        "attendees": [
            {"email": "john@example.com", "responseStatus": "accepted"}
        ]
    }
    assert json.loads(result) == expected

@pytest.mark.asyncio
@patch("src.tools.calendar_tools.get_credentials", new_callable=AsyncMock)
@patch("src.tools.calendar_tools.build", new_callable=MagicMock)
async def test_list_calendar_events_multiple_calendars(mock_build, mock_get_credentials):
    """
    Tests the list_calendar_events function with multiple calendars.
    """
    # Mock the Calendar API response for multiple calendars
    mock_service = MagicMock()
    mock_events = MagicMock()
    
    # Mock different responses for different calendars
    def mock_list_execute():
        # This would be called multiple times with different calendar IDs
        return {
            "items": [
                {
                    "id": "event1",
                    "summary": "Primary Calendar Event",
                    "start": {"dateTime": "2023-01-01T10:00:00+00:00"},
                    "end": {"dateTime": "2023-01-01T11:00:00+00:00"}
                }
            ]
        }
    
    mock_list = MagicMock()
    mock_list.execute.side_effect = mock_list_execute
    mock_events.list.return_value = mock_list
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function with multiple calendar IDs
    result = await list_calendar_events(
        calendar_ids=["primary", "work@company.com"],
        start_time="2023-01-01T00:00:00Z",
        end_time="2023-01-02T00:00:00Z"
    )

    # Assert that the function was called for each calendar
    assert mock_events.list.call_count == 2
