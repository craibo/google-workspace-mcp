import json
import asyncio
from typing import List, Optional
from datetime import datetime, date
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.auth import get_credentials
from src.config import validate_task_list_id, get_default_task_list_id, get_default_task_max_results
from src.mcp_instance import mcp

@mcp.tool()
async def list_task_lists() -> str:
    """
    Lists all available task lists for the authenticated user.
    
    Returns:
        A JSON string representing a list of task lists.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "tasks", "v1", credentials=creds)
        
        def _list_task_lists():
            return service.tasklists().list().execute()

        task_lists_result = await asyncio.to_thread(_list_task_lists)
        task_lists = task_lists_result.get("items", [])
        
        # Extract relevant information
        task_list_info = []
        for task_list in task_lists:
            task_list_info.append({
                "id": task_list.get("id"),
                "title": task_list.get("title"),
                "updated": task_list.get("updated")
            })
        
        return json.dumps(task_list_info)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def list_tasks(task_list_id: Optional[str] = None, max_results: Optional[int] = None) -> str:
    """
    Lists all tasks from a specified task list.
    
    Args:
        task_list_id: The ID of the task list (optional, defaults to configured default).
        max_results: Maximum number of tasks to return (optional, defaults to configured default).
    
    Returns:
        A JSON string representing a list of tasks.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "tasks", "v1", credentials=creds)
        
        # Use provided task list ID or default
        if task_list_id is None:
            task_list_id = get_default_task_list_id()
        
        # Validate task list ID
        validated_task_list_id = validate_task_list_id(task_list_id)
        
        # Use provided max results or default
        if max_results is None:
            max_results = get_default_task_max_results()
        
        def _list_tasks():
            return service.tasks().list(
                tasklist=validated_task_list_id,
                maxResults=max_results,
                showCompleted=False,
                showHidden=False
            ).execute()

        tasks_result = await asyncio.to_thread(_list_tasks)
        tasks = tasks_result.get("items", [])
        
        # Add task list ID to each task
        for task in tasks:
            task["taskListId"] = validated_task_list_id
        
        return json.dumps(tasks)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def search_tasks(query: str, task_list_id: Optional[str] = None, max_results: Optional[int] = None) -> str:
    """
    Searches for tasks by text query within a specified task list.
    
    Args:
        query: The text to search for in task titles and notes.
        task_list_id: The ID of the task list (optional, defaults to configured default).
        max_results: Maximum number of tasks to return (optional, defaults to configured default).
    
    Returns:
        A JSON string representing a list of matching tasks.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "tasks", "v1", credentials=creds)
        
        # Use provided task list ID or default
        if task_list_id is None:
            task_list_id = get_default_task_list_id()
        
        # Validate task list ID
        validated_task_list_id = validate_task_list_id(task_list_id)
        
        # Use provided max results or default
        if max_results is None:
            max_results = get_default_task_max_results()
        
        def _search_tasks():
            return service.tasks().list(
                tasklist=validated_task_list_id,
                maxResults=max_results,
                showCompleted=False,
                showHidden=False
            ).execute()

        tasks_result = await asyncio.to_thread(_search_tasks)
        all_tasks = tasks_result.get("items", [])
        
        # Filter tasks by query (Google Tasks API doesn't support server-side search)
        matching_tasks = []
        query_lower = query.lower()
        
        for task in all_tasks:
            title = task.get("title", "").lower()
            notes = task.get("notes", "").lower()
            
            if query_lower in title or query_lower in notes:
                task["taskListId"] = validated_task_list_id
                matching_tasks.append(task)
                
                if len(matching_tasks) >= max_results:
                    break
        
        return json.dumps(matching_tasks)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def search_tasks_by_period(start_date: str, end_date: str, task_list_id: Optional[str] = None, max_results: Optional[int] = None) -> str:
    """
    Searches for tasks within a specified date range.
    
    Args:
        start_date: Start date in ISO 8601 format (YYYY-MM-DD).
        end_date: End date in ISO 8601 format (YYYY-MM-DD).
        task_list_id: The ID of the task list (optional, defaults to configured default).
        max_results: Maximum number of tasks to return (optional, defaults to configured default).
    
    Returns:
        A JSON string representing a list of tasks within the date range.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "tasks", "v1", credentials=creds)
        
        # Use provided task list ID or default
        if task_list_id is None:
            task_list_id = get_default_task_list_id()
        
        # Validate task list ID
        validated_task_list_id = validate_task_list_id(task_list_id)
        
        # Use provided max results or default
        if max_results is None:
            max_results = get_default_task_max_results()
        
        def _list_tasks():
            return service.tasks().list(
                tasklist=validated_task_list_id,
                maxResults=max_results,
                showCompleted=False,
                showHidden=False
            ).execute()

        tasks_result = await asyncio.to_thread(_list_tasks)
        all_tasks = tasks_result.get("items", [])
        
        # Filter tasks by date range
        matching_tasks = []
        start_dt = datetime.fromisoformat(start_date).date()
        end_dt = datetime.fromisoformat(end_date).date()
        
        for task in all_tasks:
            due_date_str = task.get("due")
            if due_date_str:
                try:
                    # Parse the due date (Google Tasks API returns RFC 3339 format)
                    due_dt = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
                    if start_dt <= due_dt <= end_dt:
                        task["taskListId"] = validated_task_list_id
                        matching_tasks.append(task)
                        
                        if len(matching_tasks) >= max_results:
                            break
                except ValueError:
                    # Skip tasks with invalid date formats
                    continue
        
        return json.dumps(matching_tasks)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def create_task(title: str, task_list_id: Optional[str] = None, description: Optional[str] = None, 
                     due_date: Optional[str] = None, parent_task_id: Optional[str] = None) -> str:
    """
    Creates a new task or sub-task.
    
    Args:
        title: The title of the task.
        task_list_id: The ID of the task list (optional, defaults to configured default).
        description: Optional description/notes for the task.
        due_date: Optional due date in ISO 8601 format (YYYY-MM-DD).
        parent_task_id: Optional ID of the parent task for creating sub-tasks.
    
    Returns:
        A JSON string representing the created task.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "tasks", "v1", credentials=creds)
        
        # Use provided task list ID or default
        if task_list_id is None:
            task_list_id = get_default_task_list_id()
        
        # Validate task list ID
        validated_task_list_id = validate_task_list_id(task_list_id)
        
        # Prepare task body
        task_body = {
            "title": title
        }
        
        if description:
            task_body["notes"] = description
        
        if due_date:
            # Convert to RFC 3339 format for Google Tasks API
            try:
                due_dt = datetime.fromisoformat(due_date)
                task_body["due"] = due_dt.isoformat() + "Z"
            except ValueError:
                return json.dumps({"error": "Invalid date format. Use YYYY-MM-DD format."})
        
        if parent_task_id:
            task_body["parent"] = parent_task_id
        
        def _create_task():
            return service.tasks().insert(
                tasklist=validated_task_list_id,
                body=task_body
            ).execute()

        created_task = await asyncio.to_thread(_create_task)
        created_task["taskListId"] = validated_task_list_id
        
        return json.dumps(created_task)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def update_task(task_id: str, task_list_id: Optional[str] = None, title: Optional[str] = None,
                     description: Optional[str] = None, due_date: Optional[str] = None, 
                     status: Optional[str] = None) -> str:
    """
    Updates an existing task.
    
    Args:
        task_id: The ID of the task to update.
        task_list_id: The ID of the task list (optional, defaults to configured default).
        title: New title for the task (optional).
        description: New description/notes for the task (optional).
        due_date: New due date in ISO 8601 format (YYYY-MM-DD) (optional).
        status: New status for the task - 'needsAction' or 'completed' (optional).
    
    Returns:
        A JSON string representing the updated task.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "tasks", "v1", credentials=creds)
        
        # Use provided task list ID or default
        if task_list_id is None:
            task_list_id = get_default_task_list_id()
        
        # Validate task list ID
        validated_task_list_id = validate_task_list_id(task_list_id)
        
        # Prepare update body
        update_body = {}
        
        if title is not None:
            update_body["title"] = title
        
        if description is not None:
            update_body["notes"] = description
        
        if due_date is not None:
            # Convert to RFC 3339 format for Google Tasks API
            try:
                due_dt = datetime.fromisoformat(due_date)
                update_body["due"] = due_dt.isoformat() + "Z"
            except ValueError:
                return json.dumps({"error": "Invalid date format. Use YYYY-MM-DD format."})
        
        if status is not None:
            if status not in ["needsAction", "completed"]:
                return json.dumps({"error": "Invalid status. Use 'needsAction' or 'completed'."})
            update_body["status"] = status
        
        def _update_task():
            return service.tasks().patch(
                tasklist=validated_task_list_id,
                task=task_id,
                body=update_body
            ).execute()

        updated_task = await asyncio.to_thread(_update_task)
        updated_task["taskListId"] = validated_task_list_id
        
        return json.dumps(updated_task)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})

@mcp.tool()
async def mark_task_completed(task_id: str, task_list_id: Optional[str] = None, completed: bool = True) -> str:
    """
    Marks a task as completed or incomplete.
    
    Args:
        task_id: The ID of the task to update.
        task_list_id: The ID of the task list (optional, defaults to configured default).
        completed: Whether to mark the task as completed (True) or incomplete (False).
    
    Returns:
        A JSON string representing the updated task.
    """
    creds = await asyncio.to_thread(get_credentials)
    try:
        service = await asyncio.to_thread(build, "tasks", "v1", credentials=creds)
        
        # Use provided task list ID or default
        if task_list_id is None:
            task_list_id = get_default_task_list_id()
        
        # Validate task list ID
        validated_task_list_id = validate_task_list_id(task_list_id)
        
        # Prepare update body
        update_body = {
            "status": "completed" if completed else "needsAction"
        }
        
        if completed:
            # Set completion time to now
            update_body["completed"] = datetime.utcnow().isoformat() + "Z"
        
        def _update_task():
            return service.tasks().patch(
                tasklist=validated_task_list_id,
                task=task_id,
                body=update_body
            ).execute()

        updated_task = await asyncio.to_thread(_update_task)
        updated_task["taskListId"] = validated_task_list_id
        
        return json.dumps(updated_task)
    except HttpError as error:
        return json.dumps({"error": f"An error occurred: {error}"})
