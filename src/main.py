from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from src.tools import calendar_tools, drive_tools, gmail_tools

# Initialize the FastAPI application
app = FastAPI(
    title="Google Workspace MCP Server",
    description="A server to interact with Google Workspace services.",
    version="1.0.0",
)

# Define the request body model for tool calls
class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

# Map tool names to their corresponding functions
TOOL_MAPPING = {
    "search_drive": drive_tools.search_drive,
    "get_drive_file_details": drive_tools.get_drive_file_details,
    "search_gmail": gmail_tools.search_gmail,
    "get_gmail_message_details": gmail_tools.get_gmail_message_details,
    "search_calendar_events": calendar_tools.search_calendar_events,
    "get_calendar_event_details": calendar_tools.get_calendar_event_details,
}

@app.post("/mcp/call")
async def call_tool(request: ToolRequest):
    """
    Handles a request to call a specific tool with the given parameters.
    """
    tool_function = TOOL_MAPPING.get(request.tool_name)

    if not tool_function:
        raise HTTPException(
            status_code=400,
            detail=f"Tool '{request.tool_name}' not found."
        )

    try:
        result = tool_function(**request.parameters)
        return {"result": result}
    except TypeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parameters for tool '{request.tool_name}': {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {e}"
        )

