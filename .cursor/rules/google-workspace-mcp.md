# Google Workspace MCP Server - Complete Implementation Guide

This document provides the complete architecture and implementation guide for the Google Workspace MCP (Model-Context-Protocol) server.

## **Project Overview**

The Google Workspace MCP Server is a production-ready bridge between large language models and Google Workspace services. It provides secure, read-only access to Google Drive, Gmail, Google Calendar, and Google Tasks through a standardized MCP interface.

### **Key Features**

- **Google Drive**: File search, content retrieval, and advanced content-based searches across multiple file types
- **Gmail**: Email search, message details, and comprehensive label management
- **Google Calendar**: Calendar and event management with configurable smart defaults
- **Google Tasks**: Complete task management with CRUD operations and advanced search capabilities
- **OAuth 2.0**: Secure authentication with proper scope management
- **MCP Protocol**: Native MCP implementation for seamless agent integration
- **Docker Support**: Containerized deployment for production environments
- **Configurable Defaults**: Environment-based configuration for calendars and task lists

### **Implementation Status**

✅ **Production Ready** - All features implemented and tested:
- **53 passing tests** with comprehensive coverage
- **25+ MCP tools** across all Google Workspace services
- **Async/await patterns** throughout for optimal performance
- **Complete OAuth 2.0 integration** with all required scopes
- **Docker deployment** ready for production use

---

## **Project Setup & Authentication**

### **Prerequisites**

- Google Cloud account with billing enabled
- Python 3.10+ for local development
- Docker and Docker Compose for containerized deployment

### **Google Cloud Project Setup**

#### **Step 1: Create Google Cloud Project**

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project drop-down and select "New Project"
3. Enter project name (e.g., "google-workspace-mcp") and click "Create"
4. Select the new project from the project drop-down

#### **Step 2: Enable Required APIs**

Navigate to "APIs & Services" > "Library" and enable these APIs:

- **Google Drive API** - Search for "Google Drive API" and click "Enable"
- **Gmail API** - Search for "Gmail API" and click "Enable"  
- **Google Calendar API** - Search for "Google Calendar API" and click "Enable"
- **Google Tasks API** - Search for "Tasks API" and click "Enable"

#### **Step 3: Configure OAuth Consent Screen**

1. Navigate to "APIs & Services" > "OAuth consent screen"
2. Choose **External** and click "Create"
3. Fill in required fields:
   - **App name**: Google Workspace MCP Server
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
4. Click "SAVE AND CONTINUE"

#### **Step 4: Configure OAuth Scopes**

1. On the "Scopes" page, click "ADD OR REMOVE SCOPES"
2. Find and add these scopes:
   - `https://www.googleapis.com/auth/drive.readonly` (View files in your Google Drive)
   - `https://www.googleapis.com/auth/gmail.readonly` (Read all resources and their metadata)
   - `https://www.googleapis.com/auth/calendar.readonly` (View events on all your calendars)
   - `https://www.googleapis.com/auth/tasks` (Manage your tasks)
3. Click "Update", then "SAVE AND CONTINUE"

#### **Step 5: Add Test Users**

1. On the "Test users" page, click "+ ADD USERS"
2. Add your Google account email address (the account whose data you'll access)
3. Click "SAVE AND CONTINUE"

#### **Step 6: Create OAuth 2.0 Credentials**

1. Navigate to "APIs & Services" > "Credentials"
2. Click "+ CREATE CREDENTIALS" > "OAuth client ID"
3. Select **Desktop app** as application type
4. Name it "Google Workspace MCP Server"
5. Click "CREATE"
6. Download the JSON file and rename it to `credentials.json`
7. Place `credentials.json` in the project root directory

---

## **Project Architecture**

### **File Structure**

```
google-workspace-mcp/
├── .cursor/rules/           # Development documentation
│   ├── index.mdc           # Development guide
│   ├── python.mdc          # Coding standards
│   └── google-workspace-mcp.md  # This file
├── src/
│   ├── __init__.py
│   ├── server.py           # MCP server entry point
│   ├── mcp_instance.py     # FastMCP server instance
│   ├── auth.py             # Google OAuth handling
│   ├── config.py           # Configuration management
│   └── tools/              # MCP tool implementations
│       ├── __init__.py
│       ├── drive_tools.py      # Google Drive tools
│       ├── gmail_tools.py      # Gmail tools
│       ├── calendar_tools.py   # Calendar tools
│       └── tasks_tools.py      # Google Tasks tools
├── tests/                  # Comprehensive test suite
│   ├── test_calendar_tools.py
│   ├── test_drive_tools.py
│   ├── test_gmail_tools.py
│   ├── test_tasks_tools.py
│   └── test_config.py
├── credentials.json        # Google OAuth credentials
├── token.json             # Generated OAuth tokens
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Container orchestration
├── pytest.ini           # Test configuration
└── README.md            # User documentation
```

### **Dependencies**

```python
# requirements.txt
google-api-python-client  # Google API client library
google-auth-httplib2     # OAuth2 transport
google-auth-oauthlib     # OAuth2 flow
pydantic                 # Data validation
mcp                      # Model Context Protocol
pytest                   # Testing framework
pytest-asyncio           # Async testing support
PyPDF2                   # PDF content extraction
```

---

## **MCP Tools Documentation**

### **Google Drive Tools**

#### **1. search_drive(query: str) -> str**
- **Purpose**: Search for files in Google Drive using Google's search syntax
- **Parameters**: 
  - `query`: Search string (supports file names, content, types, etc.)
- **Returns**: JSON array of file objects with id, name, mimeType
- **Example**: `search_drive("project plan type:document")`

#### **2. get_drive_file_details(file_id: str) -> str**
- **Purpose**: Retrieve metadata and content of a specific file
- **Parameters**: 
  - `file_id`: Unique Google Drive file ID
- **Returns**: JSON object with file metadata and content
- **Supports**: Google Docs, Sheets, Slides (exported as plain text)

#### **3. search_drive_by_content(search_term: str, ...) -> str**
- **Purpose**: Advanced content-based search across multiple file types
- **Parameters**:
  - `search_term`: Text to search for within file content
  - `folder_id`: Optional folder scope
  - `file_types`: Optional MIME type filters
  - `case_sensitive`: Case-sensitive matching
  - `use_regex`: Regular expression support
  - `max_results`: Result limit
- **Returns**: JSON array with files and content snippets
- **Supports**: Google Docs, PDFs, plain text, CSV, DOCX files

#### **4. search_within_file_content(file_id: str, search_term: str, ...) -> str**
- **Purpose**: Search for specific content within a single file
- **Parameters**:
  - `file_id`: Target file ID
  - `search_term`: Text to search for
  - `case_sensitive`: Case-sensitive matching
  - `use_regex`: Regular expression support
- **Returns**: JSON object with search results and snippets

### **Gmail Tools**

#### **1. search_gmail(query: str, label_ids: Optional[List[str]], max_results: int) -> str**
- **Purpose**: Search emails using Gmail's search syntax
- **Parameters**:
  - `query`: Gmail search query
  - `label_ids`: Optional label filters
  - `max_results`: Maximum results (default: 10)
- **Returns**: JSON array of email message objects

#### **2. get_gmail_message_details(message_id: str) -> str**
- **Purpose**: Retrieve full details of a specific email
- **Parameters**: 
  - `message_id`: Gmail message ID
- **Returns**: JSON object with complete email details

#### **3. list_gmail_labels() -> str**
- **Purpose**: List all available Gmail labels
- **Returns**: JSON array of label objects with id, name, type

#### **4. search_gmail_labels(query: str) -> str**
- **Purpose**: Search Gmail labels by name
- **Parameters**: 
  - `query`: Label name search term
- **Returns**: JSON array of matching labels

#### **5. get_gmail_label_details(label_id: str) -> str**
- **Purpose**: Get detailed information about a specific label
- **Parameters**: 
  - `label_id`: Gmail label ID
- **Returns**: JSON object with label details

#### **6. search_gmail_by_label(label_id: str, query: str, max_results: int) -> str**
- **Purpose**: Search emails within a specific label
- **Parameters**:
  - `label_id`: Target label ID
  - `query`: Optional search query
  - `max_results`: Maximum results (default: 10)
- **Returns**: JSON array of emails in the label

### **Google Calendar Tools**

#### **1. list_calendars() -> str**
- **Purpose**: List all available calendars for the user
- **Returns**: JSON array of calendar objects with id, summary, description, accessRole

#### **2. list_calendar_events(...) -> str**
- **Purpose**: List events from calendars within a time period
- **Parameters**:
  - `calendar_ids`: Optional list of calendar IDs (defaults to configured)
  - `start_time`: Start time in ISO 8601 format
  - `end_time`: End time in ISO 8601 format
  - `query`: Optional text filter
  - `max_results`: Maximum results (default: 100)
- **Returns**: JSON array of event objects

#### **3. search_calendar_events(...) -> str**
- **Purpose**: Search calendar events by text within time range
- **Parameters**:
  - `calendar_ids`: Optional list of calendar IDs (defaults to configured)
  - `query`: Search text
  - `start_time`: Start time in ISO 8601 format
  - `end_time`: End time in ISO 8601 format
- **Returns**: JSON array of matching events

#### **4. get_calendar_event_details(event_id: str, calendar_id: Optional[str]) -> str**
- **Purpose**: Get full details of a specific calendar event
- **Parameters**:
  - `event_id`: Calendar event ID
  - `calendar_id`: Optional calendar ID (defaults to configured)
- **Returns**: JSON object with complete event details

### **Google Tasks Tools**

#### **1. list_task_lists() -> str**
- **Purpose**: List all available task lists for the user
- **Returns**: JSON array of task list objects with id, title, updated

#### **2. list_tasks(task_list_id: Optional[str], max_results: Optional[int]) -> str**
- **Purpose**: List all tasks from a specific task list
- **Parameters**:
  - `task_list_id`: Optional task list ID (defaults to configured)
  - `max_results`: Optional result limit (defaults to configured)
- **Returns**: JSON array of task objects

#### **3. search_tasks(query: str, task_list_id: Optional[str], max_results: Optional[int]) -> str**
- **Purpose**: Search tasks by text in titles and notes
- **Parameters**:
  - `query`: Search text
  - `task_list_id`: Optional task list ID (defaults to configured)
  - `max_results`: Optional result limit (defaults to configured)
- **Returns**: JSON array of matching tasks

#### **4. search_tasks_by_period(start_date: str, end_date: str, ...) -> str**
- **Purpose**: Find tasks with due dates within a date range
- **Parameters**:
  - `start_date`: Start date in YYYY-MM-DD format
  - `end_date`: End date in YYYY-MM-DD format
  - `task_list_id`: Optional task list ID (defaults to configured)
  - `max_results`: Optional result limit (defaults to configured)
- **Returns**: JSON array of tasks within date range

#### **5. create_task(title: str, ...) -> str**
- **Purpose**: Create a new task or sub-task
- **Parameters**:
  - `title`: Task title (required)
  - `task_list_id`: Optional task list ID (defaults to configured)
  - `description`: Optional task description/notes
  - `due_date`: Optional due date in YYYY-MM-DD format
  - `parent_task_id`: Optional parent task ID for sub-tasks
- **Returns**: JSON object of created task

#### **6. update_task(task_id: str, ...) -> str**
- **Purpose**: Update properties of an existing task
- **Parameters**:
  - `task_id`: Task ID to update (required)
  - `task_list_id`: Optional task list ID (defaults to configured)
  - `title`: Optional new title
  - `description`: Optional new description
  - `due_date`: Optional new due date in YYYY-MM-DD format
  - `status`: Optional new status ("needsAction" or "completed")
- **Returns**: JSON object of updated task

#### **7. mark_task_completed(task_id: str, task_list_id: Optional[str], completed: bool) -> str**
- **Purpose**: Mark a task as completed or incomplete
- **Parameters**:
  - `task_id`: Task ID to update (required)
  - `task_list_id`: Optional task list ID (defaults to configured)
  - `completed`: True to mark completed, False to mark incomplete (default: True)
- **Returns**: JSON object of updated task with completion status

---

## **Configuration Management**

### **Environment Variables**

#### **Calendar Configuration**
- `DEFAULT_CALENDAR_IDS`: Comma-separated list of calendar IDs (default: "primary")
- Example: `"primary,work@company.com,personal@gmail.com"`

#### **Tasks Configuration**
- `DEFAULT_TASK_LIST_ID`: Default task list ID (default: "@default")
- `MAX_TASK_SEARCH_RESULTS`: Maximum task search results (default: 100)
- `DEFAULT_TASK_MAX_RESULTS`: Default task listing limit (default: 100)

#### **Content Search Configuration**
- `MAX_CONTENT_SEARCH_RESULTS`: Maximum content search results (default: 50)
- `CONTENT_SEARCH_SNIPPET_LENGTH`: Content snippet length in characters (default: 200)

### **MCP Client Configuration**

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "/path/to/python",
      "args": ["server.py"],
      "workingDirectory": "/path/to/google-workspace-mcp",
      "env": {
        "DEFAULT_CALENDAR_IDS": "primary,work@company.com",
        "DEFAULT_TASK_LIST_ID": "@default",
        "MAX_TASK_SEARCH_RESULTS": "100",
        "DEFAULT_TASK_MAX_RESULTS": "100",
        "MAX_CONTENT_SEARCH_RESULTS": "50",
        "CONTENT_SEARCH_SNIPPET_LENGTH": "200"
      }
    }
  }
}
```

---

## **Implementation Details**

### **Authentication (src/auth.py)**

- **Function**: `get_credentials() -> Credentials`
- **Purpose**: Manages OAuth 2.0 flow and token refresh
- **Flow**: 
  1. Checks for existing `token.json`
  2. Validates token expiration
  3. Initiates browser OAuth flow if needed
  4. Saves refreshed tokens

### **MCP Server (src/server.py & src/mcp_instance.py)**

- **Framework**: FastMCP (official Python MCP implementation)
- **Protocol**: Model Context Protocol over stdio
- **Tools**: Auto-discovered via `@mcp.tool()` decorators
- **Async**: All tools use `asyncio.to_thread()` for non-blocking API calls

### **Error Handling**

- **Google API Errors**: Comprehensive `HttpError` exception handling
- **Input Validation**: Parameter validation with descriptive error messages
- **Async Safety**: Proper async/await patterns throughout
- **Graceful Degradation**: Fallback to defaults when optional parameters missing

### **Performance Optimizations**

- **Async Operations**: All Google API calls are non-blocking
- **Connection Pooling**: Efficient credential reuse
- **Lazy Loading**: Services instantiated only when needed
- **Caching**: Token caching with automatic refresh

---

## **Docker Deployment**

### **Dockerfile**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY credentials.json ./

# Run MCP server
CMD ["python", "server.py"]
```

### **docker-compose.yml**

```yaml
version: '3.8'

services:
  google-workspace-mcp:
    build: .
    container_name: google-workspace-mcp
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - token_data:/app/
    stdin_open: true
    tty: true

volumes:
  token_data:
```

### **Production Deployment**

1. **Build the container**:
   ```bash
   docker-compose build
   ```

2. **Run initial OAuth flow**:
   ```bash
   docker-compose run --rm google-workspace-mcp python -c "from src.auth import get_credentials; get_credentials()"
   ```

3. **Deploy the server**:
   ```bash
   docker-compose up -d
   ```

---

## **Testing**

### **Test Suite Coverage**

- **53 total tests** across all components
- **Unit tests** for all MCP tools
- **Integration tests** with mocked Google APIs  
- **Configuration tests** for environment variables
- **Error handling tests** for edge cases

### **Running Tests**

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_tasks_tools.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### **Test Structure**

```
tests/
├── test_calendar_tools.py    # Calendar MCP tools tests
├── test_drive_tools.py       # Drive MCP tools tests  
├── test_gmail_tools.py       # Gmail MCP tools tests
├── test_tasks_tools.py       # Tasks MCP tools tests
├── test_config.py           # Configuration tests
└── conftest.py              # Test fixtures and setup
```

---

## **Security Considerations**

### **OAuth 2.0 Security**

- **Minimal Scopes**: Only required permissions requested
- **Token Storage**: Secure local token storage with automatic refresh
- **Credential Protection**: `credentials.json` should be treated as sensitive
- **HTTPS Only**: All Google API communications over HTTPS

### **Production Security**

- **Container Security**: Use minimal base images and non-root users
- **Secret Management**: Use Docker secrets or environment injection for credentials
- **Network Security**: Restrict container network access
- **Logging**: Avoid logging sensitive authentication data

### **Data Privacy**

- **Read-Only Access**: No modification of user data (except Tasks CRUD operations)
- **Local Processing**: All data processing happens locally
- **No Data Persistence**: No user data stored beyond session
- **Audit Trail**: Comprehensive logging of API calls

---

## **Troubleshooting**

### **Common Issues**

#### **1. Authentication Errors**
- **Problem**: "The file token.json not found" or "Invalid credentials"
- **Solution**: Run initial OAuth flow or regenerate credentials.json

#### **2. API Quota Exceeded**  
- **Problem**: "Quota exceeded" errors from Google APIs
- **Solution**: Check Google Cloud Console quotas and request increases if needed

#### **3. Permission Denied**
- **Problem**: "Insufficient Permission" errors
- **Solution**: Verify OAuth scopes match required permissions

#### **4. Docker Issues**
- **Problem**: Container fails to start or access credentials
- **Solution**: Verify volume mounts and file permissions

### **Debug Mode**

Enable debug logging by setting environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
export MCP_DEBUG=1
python server.py
```

---

## **Development Guidelines**

### **Code Standards**

- **Python Style**: Follow PEP 8 with functional programming patterns
- **Async Patterns**: Use `async`/`await` for all I/O operations
- **Type Hints**: Comprehensive type annotations
- **Error Handling**: Graceful error handling with user-friendly messages

### **Adding New Tools**

1. **Create tool function** in appropriate `src/tools/` file
2. **Add `@mcp.tool()` decorator** with proper docstring
3. **Implement async pattern** using `asyncio.to_thread()`
4. **Add comprehensive tests** in `tests/` directory
5. **Update documentation** in README.md

### **Testing New Features**

1. **Write tests first** (TDD approach)
2. **Mock Google API calls** using `unittest.mock`
3. **Test error scenarios** and edge cases
4. **Verify async behavior** with `pytest-asyncio`

---

## **Conclusion**

The Google Workspace MCP Server is a production-ready solution that provides secure, efficient access to Google Workspace services through the Model Context Protocol. With comprehensive testing, Docker support, and extensive configuration options, it's ready for both development and production deployment.

The server successfully bridges the gap between large language models and Google Workspace, enabling powerful automation and data access scenarios while maintaining security and performance best practices.
