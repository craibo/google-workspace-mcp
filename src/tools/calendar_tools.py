import json
import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.auth import get_credentials
from src.mcp_instance import mcp

@mcp.tool()
async def search_calendar_events(query: str, start_time: str, end_time: str) -> str:
    """
    Searches for calendar events within a specified time range that match a query.

    Args:
        query: The text to search for in event summaries and descriptions.
        start_time: The start of the time window in ISO 8601 format.
        end_time: The end of the time window in ISO 8601 format.

    Returns:
        A JSON string representing a list of events.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "calendar", "v3", credentials=creds)
        
        def _search():
            return service.events().list(
                calendarId="primary",
                q=query,
                timeMin=start_time,
                timeMax=end_time,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

        events_result = await asyncio.to_thread(_search)
        events = events_result.get("items", [])
        return json.dumps(events)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def get_calendar_event_details(event_id: str) -> str:
    """
    Fetches the full details of a specific calendar event.

    Args:
        event_id: The unique ID of the event.

    Returns:
        A JSON string with event details.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "calendar", "v3", credentials=creds)
        
        def _get_details():
            return service.events().get(calendarId="primary", eventId=event_id).execute()

        event = await asyncio.to_thread(_get_details)
        return json.dumps(event)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
