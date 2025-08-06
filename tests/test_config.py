import pytest
import os
from unittest.mock import patch

from src.config import get_default_calendar_ids, validate_calendar_ids

def test_get_default_calendar_ids_default():
    """
    Tests get_default_calendar_ids with no environment variable set.
    """
    with patch.dict(os.environ, {}, clear=True):
        result = get_default_calendar_ids()
        assert result == ["primary"]

def test_get_default_calendar_ids_single():
    """
    Tests get_default_calendar_ids with a single calendar ID.
    """
    with patch.dict(os.environ, {"DEFAULT_CALENDAR_IDS": "work@company.com"}):
        result = get_default_calendar_ids()
        assert result == ["work@company.com"]

def test_get_default_calendar_ids_multiple():
    """
    Tests get_default_calendar_ids with multiple calendar IDs.
    """
    with patch.dict(os.environ, {"DEFAULT_CALENDAR_IDS": "primary,work@company.com,personal@gmail.com"}):
        result = get_default_calendar_ids()
        assert result == ["primary", "work@company.com", "personal@gmail.com"]

def test_get_default_calendar_ids_with_spaces():
    """
    Tests get_default_calendar_ids with spaces in the environment variable.
    """
    with patch.dict(os.environ, {"DEFAULT_CALENDAR_IDS": " primary , work@company.com "}):
        result = get_default_calendar_ids()
        assert result == ["primary", "work@company.com"]

def test_validate_calendar_ids_empty():
    """
    Tests validate_calendar_ids with empty list.
    """
    with patch.dict(os.environ, {"DEFAULT_CALENDAR_IDS": "primary,work@company.com"}):
        result = validate_calendar_ids([])
        assert result == ["primary", "work@company.com"]

def test_validate_calendar_ids_valid():
    """
    Tests validate_calendar_ids with valid calendar IDs.
    """
    result = validate_calendar_ids(["primary", "work@company.com"])
    assert result == ["primary", "work@company.com"]

def test_validate_calendar_ids_duplicates():
    """
    Tests validate_calendar_ids with duplicate calendar IDs.
    """
    result = validate_calendar_ids(["primary", "primary", "work@company.com"])
    assert result == ["primary", "work@company.com"]

def test_validate_calendar_ids_with_spaces():
    """
    Tests validate_calendar_ids with calendar IDs containing spaces.
    """
    result = validate_calendar_ids([" primary ", " work@company.com "])
    assert result == ["primary", "work@company.com"]

def test_validate_calendar_ids_empty_strings():
    """
    Tests validate_calendar_ids with empty strings.
    """
    with patch.dict(os.environ, {"DEFAULT_CALENDAR_IDS": "primary,work@company.com"}):
        result = validate_calendar_ids(["", "primary", "", "work@company.com"])
        assert result == ["primary", "work@company.com"] 