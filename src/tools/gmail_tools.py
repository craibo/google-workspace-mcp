import json
import base64
import asyncio
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.auth import get_credentials
from src.mcp_instance import mcp

@mcp.tool()
async def search_gmail(query: str) -> str:
    """
    Searches for emails in Gmail matching the query.

    Args:
        query: The search string.

    Returns:
        A JSON string representing a list of email messages.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "gmail", "v1", credentials=creds)

        def _search():
            return service.users().messages().list(userId="me", q=query).execute()

        result = await asyncio.to_thread(_search)
        messages = result.get("messages", [])
        
        message_list = []
        for msg in messages[:10]:
            def _get_message():
                return service.users().messages().get(userId="me", id=msg["id"]).execute()
            
            msg_data = await asyncio.to_thread(_get_message)
            headers = msg_data["payload"]["headers"]
            
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
            from_email = next((h["value"] for h in headers if h["name"] == "From"), "")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "")

            message_list.append({
                "id": msg_data["id"],
                "subject": subject,
                "from": from_email,
                "date": date,
            })
            
        return json.dumps(message_list)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def get_gmail_message_details(message_id: str) -> str:
    """
    Fetches the full details of a specific email message by its ID.

    Args:
        message_id: The unique ID of the email message.

    Returns:
        A JSON string with email details.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "gmail", "v1", credentials=creds)
        
        def _get_details():
            return service.users().messages().get(userId="me", id=message_id).execute()

        msg_data = await asyncio.to_thread(_get_details)
        headers = msg_data["payload"]["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        from_email = next((h["value"] for h in headers if h["name"] == "From"), "")
        to_email = next((h["value"] for h in headers if h["name"] == "To"), "")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "")
        
        body = ""
        if "parts" in msg_data["payload"]:
            for part in msg_data["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    body_data = part["body"].get("data")
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                        break
        else:
            body_data = msg_data["payload"]["body"].get("data")
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode("utf-8")

        message_details = {
            "id": msg_data["id"],
            "subject": subject,
            "from": from_email,
            "to": to_email,
            "date": date,
            "body": body,
        }
        
        return json.dumps(message_details)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
