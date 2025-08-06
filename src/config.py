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