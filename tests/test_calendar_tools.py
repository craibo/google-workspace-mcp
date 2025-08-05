import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from src.tools.calendar_tools import search_calendar_events, get_calendar_event_details

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
        "items": [{"id": "123", "summary": "Test Event"}]
    }
    mock_events.list.return_value = mock_list
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function
    result = await search_calendar_events(
        "test query", "2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z"
    )

    # Assert the result
    assert json.loads(result) == [{"id": "123", "summary": "Test Event"}]

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
    mock_get.execute.return_value = {"id": "123", "summary": "Test Event"}
    mock_events.get.return_value = mock_get
    mock_service.events.return_value = mock_events
    mock_build.return_value = mock_service

    # Call the function
    result = await get_calendar_event_details("123")

    # Assert the result
    assert json.loads(result) == {"id": "123", "summary": "Test Event"}
