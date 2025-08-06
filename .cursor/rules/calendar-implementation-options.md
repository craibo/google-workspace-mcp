# Google Calendar Implementation Options

This document provides two implementation options for making calendar tools default to using configured calendar IDs while still allowing users to specify other calendar IDs when needed.

## **Option 1: Smart Default with Optional Override**

### **Overview**
This approach makes calendar IDs optional in function signatures and automatically uses defaults when not provided. It provides a single, flexible interface for each operation.

### **Implementation**
- **File**: `src/tools/calendar_tools.py` (updated)
- **Approach**: Optional parameters with smart defaults
- **Functions**: 4 main functions with optional calendar parameters

### **Function Signatures**

```python
# List events with optional calendar IDs
async def list_calendar_events(
    calendar_ids: Optional[List[str]] = None,  # Uses defaults if None
    start_time: str = None,
    end_time: str = None,
    query: Optional[str] = None,
    max_results: int = 100
) -> str

# Search events with optional calendar IDs
async def search_calendar_events(
    calendar_ids: Optional[List[str]] = None,  # Uses defaults if None
    query: str = None,
    start_time: str = None,
    end_time: str = None
) -> str

# Get event details with optional calendar ID
async def get_calendar_event_details(
    event_id: str,
    calendar_id: Optional[str] = None  # Uses first default if None
) -> str
```

### **Usage Examples**

```python
# Use default calendars (configured via DEFAULT_CALENDAR_IDS)
await list_calendar_events(
    start_time="2023-01-01T00:00:00Z",
    end_time="2023-01-02T00:00:00Z"
)

# Use specific calendars
await list_calendar_events(
    calendar_ids=["work@company.com", "personal@gmail.com"],
    start_time="2023-01-01T00:00:00Z",
    end_time="2023-01-02T00:00:00Z"
)

# Get event details from default calendar
await get_calendar_event_details("event123")

# Get event details from specific calendar
await get_calendar_event_details("event123", "work@company.com")
```

### **Pros**
- ✅ **Simple Interface**: Single function per operation
- ✅ **Backward Compatible**: Existing code works without changes
- ✅ **Flexible**: Easy to switch between defaults and specific calendars
- ✅ **Intuitive**: Natural parameter progression from optional to required

### **Cons**
- ❌ **Parameter Overload**: Functions have many optional parameters
- ❌ **Less Explicit**: Harder to distinguish between default and specific usage
- ❌ **Documentation Complexity**: Need to explain when each parameter is used

---

## **Option 2: Separate Functions for Default and Specific Calendars**

### **Overview**
This approach provides separate, explicit functions for default calendar operations vs. specific calendar operations. Each function has a clear, focused purpose.

### **Implementation**
- **File**: `src/tools/calendar_tools_v2.py` (alternative implementation)
- **Approach**: Separate functions with clear naming
- **Functions**: 8 functions (4 default + 4 specific)

### **Function Signatures**

```python
# Default calendar functions
async def list_default_calendar_events(
    start_time: str,
    end_time: str,
    query: Optional[str] = None,
    max_results: int = 100
) -> str

async def search_default_calendar_events(
    query: str,
    start_time: str,
    end_time: str
) -> str

async def get_default_calendar_event_details(event_id: str) -> str

# Specific calendar functions
async def list_specific_calendar_events(
    calendar_ids: List[str],  # Required
    start_time: str,
    end_time: str,
    query: Optional[str] = None,
    max_results: int = 100
) -> str

async def search_specific_calendar_events(
    calendar_ids: List[str],  # Required
    query: str,
    start_time: str,
    end_time: str
) -> str

async def get_specific_calendar_event_details(
    calendar_id: str,  # Required
    event_id: str
) -> str
```

### **Usage Examples**

```python
# Use default calendars
await list_default_calendar_events(
    start_time="2023-01-01T00:00:00Z",
    end_time="2023-01-02T00:00:00Z"
)

await search_default_calendar_events(
    query="meeting",
    start_time="2023-01-01T00:00:00Z",
    end_time="2023-01-02T00:00:00Z"
)

await get_default_calendar_event_details("event123")

# Use specific calendars
await list_specific_calendar_events(
    calendar_ids=["work@company.com", "personal@gmail.com"],
    start_time="2023-01-01T00:00:00Z",
    end_time="2023-01-02T00:00:00Z"
)

await search_specific_calendar_events(
    calendar_ids=["work@company.com"],
    query="meeting",
    start_time="2023-01-01T00:00:00Z",
    end_time="2023-01-02T00:00:00Z"
)

await get_specific_calendar_event_details("work@company.com", "event123")
```

### **Pros**
- ✅ **Explicit Intent**: Clear distinction between default and specific operations
- ✅ **Simple Signatures**: Each function has focused parameters
- ✅ **Self-Documenting**: Function names indicate behavior
- ✅ **Type Safety**: Required parameters prevent confusion

### **Cons**
- ❌ **More Functions**: Twice as many functions to maintain
- ❌ **Code Duplication**: Similar logic in multiple functions
- ❌ **Learning Curve**: Users need to know which function to use
- ❌ **Tool Discovery**: More tools to discover and understand

---

## **Configuration for Both Options**

Both options use the same configuration mechanism:

### **Environment Variable**
```bash
export DEFAULT_CALENDAR_IDS="primary,work@company.com,personal@gmail.com"
```

### **MCP Client Configuration**
```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "/path/to/python",
      "args": ["server.py"],
      "workingDirectory": "/path/to/project",
      "env": {
        "DEFAULT_CALENDAR_IDS": "primary,work@company.com"
      }
    }
  }
}
```

---

## **Recommendation**

### **For Option 1 (Smart Default with Optional Override)**
**Choose this if:**
- You prefer a simpler, unified interface
- You want backward compatibility
- You value flexibility over explicitness
- You have users who might not always know which calendars to use

### **For Option 2 (Separate Functions)**
**Choose this if:**
- You prefer explicit, self-documenting code
- You want clear separation of concerns
- You value type safety and required parameters
- You have users who need to be very specific about calendar selection

---

## **Testing**

Both options have comprehensive test coverage:

```bash
# Test Option 1
./.venv/bin/pytest tests/test_calendar_options.py::test_list_calendar_events_with_defaults -v
./.venv/bin/pytest tests/test_calendar_options.py::test_list_calendar_events_with_specific_calendars -v

# Test Option 2
./.venv/bin/pytest tests/test_calendar_options.py::test_list_default_calendar_events -v
./.venv/bin/pytest tests/test_calendar_options.py::test_list_specific_calendar_events -v
```

---

## **Migration Path**

### **From Current Implementation to Option 1**
- ✅ **No Breaking Changes**: Current code continues to work
- ✅ **Gradual Adoption**: Can start using defaults immediately
- ✅ **Easy Rollback**: Can always specify calendar IDs explicitly

### **From Current Implementation to Option 2**
- ⚠️ **Breaking Changes**: Need to update existing code
- ✅ **Clear Migration**: Old functions can be deprecated gradually
- ✅ **Better Organization**: Clear separation of concerns

---

## **Final Decision**

**Option 1 (Smart Default with Optional Override) has been chosen** for the following reasons:

1. **User Experience**: Most users will want to use default calendars most of the time
2. **Backward Compatibility**: Existing code continues to work without changes
3. **Flexibility**: Easy to switch between defaults and specific calendars
4. **Maintenance**: Fewer functions to maintain and test
5. **Learning Curve**: Simpler for new users to understand

The implementation is complete in `src/tools/calendar_tools.py` and all tests are passing. 