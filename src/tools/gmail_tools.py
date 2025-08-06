import json
import base64
import asyncio
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.auth import get_credentials
from src.mcp_instance import mcp

@mcp.tool()
async def search_gmail(query: str, label_ids: Optional[List[str]] = None, max_results: int = 10) -> str:
    """
    Searches for emails in Gmail matching the query, optionally within specific labels.

    Args:
        query: The search string.
        label_ids: Optional list of label IDs to search within.
        max_results: Maximum number of results to return (default: 10).

    Returns:
        A JSON string representing a list of email messages.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "gmail", "v1", credentials=creds)

        def _search():
            search_params = {"userId": "me", "q": query, "maxResults": max_results}
            if label_ids:
                search_params["labelIds"] = label_ids
            return service.users().messages().list(**search_params).execute()

        result = await asyncio.to_thread(_search)
        messages = result.get("messages", [])
        
        message_list = []
        for msg in messages:
            def _get_message():
                return service.users().messages().get(userId="me", id=msg["id"]).execute()
            
            msg_data = await asyncio.to_thread(_get_message)
            headers = msg_data["payload"]["headers"]
            
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
            from_email = next((h["value"] for h in headers if h["name"] == "From"), "")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "")
            
            # Extract labels
            labels = msg_data.get("labelIds", [])

            message_list.append({
                "id": msg_data["id"],
                "subject": subject,
                "from": from_email,
                "date": date,
                "labels": labels,
                "snippet": msg_data.get("snippet", "")
            })
            
        return json.dumps({
            "messages": message_list,
            "total_results": len(message_list),
            "query": query,
            "label_ids": label_ids
        })
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def list_gmail_labels() -> str:
    """
    Lists all available Gmail labels for the authenticated user.

    Returns:
        A JSON string representing a list of Gmail labels.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "gmail", "v1", credentials=creds)

        def _get_labels():
            return service.users().labels().list(userId="me").execute()

        result = await asyncio.to_thread(_get_labels)
        labels = result.get("labels", [])
        
        label_list = []
        for label in labels:
            label_info = {
                "id": label["id"],
                "name": label["name"],
                "type": label.get("type", "user"),
                "messageListVisibility": label.get("messageListVisibility", "show"),
                "labelListVisibility": label.get("labelListVisibility", "labelShow")
            }
            
            # Add message count if available
            if "messagesTotal" in label:
                label_info["messagesTotal"] = label["messagesTotal"]
            if "messagesUnread" in label:
                label_info["messagesUnread"] = label["messagesUnread"]
                
            label_list.append(label_info)
            
        return json.dumps({
            "labels": label_list,
            "total_labels": len(label_list)
        })
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def search_gmail_labels(query: str = "") -> str:
    """
    Searches for Gmail labels matching the query.

    Args:
        query: Optional search string to filter labels by name.

    Returns:
        A JSON string representing a list of matching Gmail labels.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "gmail", "v1", credentials=creds)

        def _get_labels():
            return service.users().labels().list(userId="me").execute()

        result = await asyncio.to_thread(_get_labels)
        all_labels = result.get("labels", [])
        
        # Filter labels by query if provided
        if query:
            query_lower = query.lower()
            matching_labels = [
                label for label in all_labels 
                if query_lower in label["name"].lower()
            ]
        else:
            matching_labels = all_labels
        
        label_list = []
        for label in matching_labels:
            label_info = {
                "id": label["id"],
                "name": label["name"],
                "type": label.get("type", "user"),
                "messageListVisibility": label.get("messageListVisibility", "show"),
                "labelListVisibility": label.get("labelListVisibility", "labelShow")
            }
            
            # Add message count if available
            if "messagesTotal" in label:
                label_info["messagesTotal"] = label["messagesTotal"]
            if "messagesUnread" in label:
                label_info["messagesUnread"] = label["messagesUnread"]
                
            label_list.append(label_info)
            
        return json.dumps({
            "labels": label_list,
            "total_labels": len(label_list),
            "query": query
        })
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def get_gmail_label_details(label_id: str) -> str:
    """
    Gets detailed information about a specific Gmail label.

    Args:
        label_id: The ID of the label to get details for.

    Returns:
        A JSON string with label details.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "gmail", "v1", credentials=creds)

        def _get_label():
            return service.users().labels().get(userId="me", id=label_id).execute()

        label_data = await asyncio.to_thread(_get_label)
        
        label_details = {
            "id": label_data["id"],
            "name": label_data["name"],
            "type": label_data.get("type", "user"),
            "messageListVisibility": label_data.get("messageListVisibility", "show"),
            "labelListVisibility": label_data.get("labelListVisibility", "labelShow")
        }
        
        # Add message counts if available
        if "messagesTotal" in label_data:
            label_details["messagesTotal"] = label_data["messagesTotal"]
        if "messagesUnread" in label_data:
            label_details["messagesUnread"] = label_data["messagesUnread"]
        if "threadsTotal" in label_data:
            label_details["threadsTotal"] = label_data["threadsTotal"]
        if "threadsUnread" in label_data:
            label_details["threadsUnread"] = label_data["threadsUnread"]
            
        return json.dumps(label_details)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def search_gmail_by_label(label_id: str, query: str = "", max_results: int = 10) -> str:
    """
    Searches for emails within a specific Gmail label.

    Args:
        label_id: The ID of the label to search within.
        query: Optional search string to filter messages.
        max_results: Maximum number of results to return (default: 10).

    Returns:
        A JSON string representing a list of email messages in the label.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "gmail", "v1", credentials=creds)

        def _search():
            search_params = {
                "userId": "me", 
                "labelIds": [label_id], 
                "maxResults": max_results
            }
            if query:
                search_params["q"] = query
            return service.users().messages().list(**search_params).execute()

        result = await asyncio.to_thread(_search)
        messages = result.get("messages", [])
        
        message_list = []
        for msg in messages:
            def _get_message():
                return service.users().messages().get(userId="me", id=msg["id"]).execute()
            
            msg_data = await asyncio.to_thread(_get_message)
            headers = msg_data["payload"]["headers"]
            
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
            from_email = next((h["value"] for h in headers if h["name"] == "From"), "")
            date = next((h["value"] for h in headers if h["name"] == "Date"), "")
            
            # Extract all labels
            labels = msg_data.get("labelIds", [])

            message_list.append({
                "id": msg_data["id"],
                "subject": subject,
                "from": from_email,
                "date": date,
                "labels": labels,
                "snippet": msg_data.get("snippet", "")
            })
            
        return json.dumps({
            "messages": message_list,
            "total_results": len(message_list),
            "label_id": label_id,
            "query": query
        })
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
        
        # Extract labels
        labels = msg_data.get("labelIds", [])
        
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
            "labels": labels,
            "snippet": msg_data.get("snippet", "")
        }
        
        return json.dumps(message_details)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
