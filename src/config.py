import os
import logging
from typing import List

logger = logging.getLogger(__name__)

def get_default_calendar_ids() -> List[str]:
    """
    Retrieves the list of default calendar IDs from environment variables.
    
    Returns:
        A list of calendar IDs to use as defaults when no specific calendar is specified.
        If no environment variable is set, returns ['primary'] as default.
    """
    default_calendars = os.getenv('DEFAULT_CALENDAR_IDS', 'primary')
    calendar_ids = [cal.strip() for cal in default_calendars.split(',') if cal.strip()]
    
    logger.info(f"Default calendar IDs: {calendar_ids}")
    return calendar_ids

def validate_calendar_ids(calendar_ids: List[str]) -> List[str]:
    """
    Validates and normalizes calendar IDs.
    
    Args:
        calendar_ids: List of calendar IDs to validate
        
    Returns:
        List of validated calendar IDs
    """
    if not calendar_ids:
        return get_default_calendar_ids()
    
    # Remove duplicates while preserving order
    seen = set()
    validated_ids = []
    for cal in calendar_ids:
        cal_stripped = cal.strip()
        if cal_stripped and cal_stripped not in seen:
            validated_ids.append(cal_stripped)
            seen.add(cal_stripped)
    
    if not validated_ids:
        logger.warning("No valid calendar IDs provided, using defaults")
        return get_default_calendar_ids()
    
    logger.info(f"Validated calendar IDs: {validated_ids}")
    return validated_ids

def get_default_task_list_id() -> str:
    """
    Retrieves the default task list ID from environment variables.
    
    Returns:
        The default task list ID to use when no specific task list is specified.
        If no environment variable is set, returns '@default' as default.
    """
    default_task_list = os.getenv('DEFAULT_TASK_LIST_ID', '@default')
    logger.info(f"Default task list ID: {default_task_list}")
    return default_task_list

def validate_task_list_id(task_list_id: str) -> str:
    """
    Validates and normalizes task list ID.
    
    Args:
        task_list_id: Task list ID to validate
        
    Returns:
        Validated task list ID
    """
    if not task_list_id or not task_list_id.strip():
        logger.warning("No task list ID provided, using default")
        return get_default_task_list_id()
    
    validated_id = task_list_id.strip()
    logger.info(f"Validated task list ID: {validated_id}")
    return validated_id

def get_supported_content_search_types() -> List[str]:
    """
    Returns the list of MIME types that support content search.
    
    Returns:
        List of MIME types that can be searched for content.
    """
    return [
        'application/vnd.google-apps.document',  # Google Docs
        'application/pdf',  # PDF files
        'text/plain',  # Plain text files
        'text/csv',  # CSV files
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # DOCX
    ]

def get_max_content_search_results() -> int:
    """
    Returns the maximum number of results for content search.
    
    Returns:
        Maximum number of search results to return.
    """
    return int(os.getenv('MAX_CONTENT_SEARCH_RESULTS', '50'))

def get_content_search_snippet_length() -> int:
    """
    Returns the length of search result snippets in characters.
    
    Returns:
        Number of characters to include in search snippets.
    """
    return int(os.getenv('CONTENT_SEARCH_SNIPPET_LENGTH', '200'))

def get_max_task_search_results() -> int:
    """
    Returns the maximum number of results for task search operations.
    
    Returns:
        Maximum number of task search results to return.
    """
    return int(os.getenv('MAX_TASK_SEARCH_RESULTS', '100'))

def get_default_task_max_results() -> int:
    """
    Returns the default maximum number of results for task listing operations.
    
    Returns:
        Default maximum number of tasks to return when listing.
    """
    return int(os.getenv('DEFAULT_TASK_MAX_RESULTS', '100')) 