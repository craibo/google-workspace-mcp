import json
import asyncio
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.auth import get_credentials
from src.config import validate_calendar_ids
from src.mcp_instance import mcp

@mcp.tool()
async def list_calendars() -> str:
    """
    Lists all available calendars for the authenticated user.
    
    Returns:
        A JSON string representing a list of calendars.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "calendar", "v3", credentials=creds)
        
        def _list_calendars():
            return service.calendarList().list().execute()

        calendar_list = await asyncio.to_thread(_list_calendars)
        calendars = calendar_list.get("items", [])
        
        # Extract relevant information
        calendar_info = []
        for calendar in calendars:
            calendar_info.append({
                "id": calendar.get("id"),
                "summary": calendar.get("summary"),
                "description": calendar.get("description", ""),
                "accessRole": calendar.get("accessRole", ""),
                "primary": calendar.get("primary", False)
            })
        
        return json.dumps(calendar_info)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def list_calendar_events(calendar_ids: List[str], start_time: str, end_time: str, query: Optional[str] = None, max_results: int = 100) -> str:
    """
    Lists all events from specified calendars within a time period, with optional filtering.
    
    Args:
        calendar_ids: List of calendar IDs to search (required).
        start_time: The start of the time window in ISO 8601 format.
        end_time: The end of the time window in ISO 8601 format.
        query: Optional text to search for in event summaries and descriptions.
        max_results: Maximum number of events to return (default: 100).
    
    Returns:
        A JSON string representing a list of events.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "calendar", "v3", credentials=creds)
        
        # Validate calendar IDs
        validated_calendar_ids = validate_calendar_ids(calendar_ids)
        
        all_events = []
        
        for calendar_id in validated_calendar_ids:
            def _list_events():
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=start_time,
                    timeMax=end_time,
                    q=query,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime"
                ).execute()
                return events_result.get("items", [])
            
            events = await asyncio.to_thread(_list_events)
            
            # Add calendar ID to each event
            for event in events:
                event["calendarId"] = calendar_id
                all_events.append(event)
        
        # Sort all events by start time
        all_events.sort(key=lambda x: x.get("start", {}).get("dateTime", x.get("start", {}).get("date", "")))
        
        return json.dumps(all_events)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def search_calendar_events(calendar_ids: List[str], query: str, start_time: str, end_time: str) -> str:
    """
    Searches for calendar events within a specified time range that match a query.
    
    Args:
        calendar_ids: List of calendar IDs to search (required).
        query: The text to search for in event summaries and descriptions.
        start_time: The start of the time window in ISO 8601 format.
        end_time: The end of the time window in ISO 8601 format.
    
    Returns:
        A JSON string representing a list of events.
    """
    # Use the list_calendar_events function with the query parameter
    return await list_calendar_events(calendar_ids, start_time, end_time, query)

@mcp.tool()
async def get_calendar_event_details(calendar_id: str, event_id: str) -> str:
    """
    Fetches the full details of a specific calendar event.
    
    Args:
        calendar_id: The ID of the calendar containing the event (required).
        event_id: The unique ID of the event.
    
    Returns:
        A JSON string with event details.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "calendar", "v3", credentials=creds)
        
        def _get_event_details():
            return service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        event = await asyncio.to_thread(_get_event_details)
        return json.dumps(event)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
