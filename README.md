# Google Workspace MCP Server

This project is a secure MCP (Model-Context-Protocol) server that acts as a bridge between a large language model (or any other agent) and Google Workspace services. It exposes a set of tools to interact with Google Drive, Gmail, Google Calendar, and Google Tasks in a read-only capacity.

This server is built using the official [Python MCP SDK](https://modelcontextprotocol.io/quickstart/server) and is ready to be used with any MCP-compatible host, such as Claude for Desktop or [Gemini CLI](https://github.com/google-gemini/gemini-cli).

## Features

-   **Google Drive**: Search for files, retrieve file content, and perform advanced content-based searches across multiple file types.
-   **Gmail**: Search for emails and fetch email details.
-   **Google Calendar**: List calendars, search events, and get event details with enhanced filtering.
-   **Google Tasks**: Manage tasks and sub-tasks with comprehensive CRUD operations and search capabilities.
-   **OAuth 2.0**: Secure authentication using Google's OAuth 2.0 flow.
-   **Dockerized**: Ready for deployment with Docker and Docker Compose.
-   **Configurable**: Support for default calendar IDs and task list IDs via environment variables.

## Available Tools

This server exposes the following tools to the agent:

### Google Drive

-   `search_drive(query: str)`: Searches for files in Google Drive matching the query.
-   `get_drive_file_details(file_id: str)`: Fetches the metadata and content of a specific file by its ID.
-   `search_drive_by_content(search_term: str, folder_id: Optional[str] = None, file_types: Optional[List[str]] = None, case_sensitive: bool = False, use_regex: bool = False, max_results: Optional[int] = None)`: Searches for files containing specific text content with advanced options.
-   `search_within_file_content(file_id: str, search_term: str, case_sensitive: bool = False, use_regex: bool = False)`: Searches for specific content within a single file.

### Gmail

-   `search_gmail(query: str, label_ids: Optional[List[str]] = None, max_results: int = 10)`: Searches for emails in Gmail matching the query, optionally within specific labels.
-   `get_gmail_message_details(message_id: str)`: Fetches the full details of a specific email message by its ID.
-   `list_gmail_labels()`: Lists all available Gmail labels for the authenticated user.
-   `search_gmail_labels(query: str = "")`: Searches for Gmail labels matching the query.
-   `get_gmail_label_details(label_id: str)`: Gets detailed information about a specific Gmail label.
-   `search_gmail_by_label(label_id: str, query: str = "", max_results: int = 10)`: Searches for emails within a specific Gmail label.

### Google Calendar

-   `list_calendars()`: Lists all available calendars for the authenticated user.
-   `list_calendar_events(calendar_ids: Optional[List[str]] = None, start_time: str, end_time: str, query: Optional[str] = None, max_results: int = 100)`: Lists all events from specified calendars within a time period, with optional filtering. If no calendar_ids are provided, uses the default configured calendars.
-   `search_calendar_events(calendar_ids: Optional[List[str]] = None, query: str, start_time: str, end_time: str)`: Searches for calendar events within a specified time range that match a query. If no calendar_ids are provided, uses the default configured calendars.
-   `get_calendar_event_details(event_id: str, calendar_id: Optional[str] = None)`: Fetches the full details of a specific calendar event. If no calendar_id is provided, uses the first configured default calendar.

### Google Tasks

-   `list_task_lists()`: Lists all available task lists for the authenticated user.
-   `list_tasks(task_list_id: Optional[str] = None, max_results: int = 100)`: Lists all tasks from a specific task list. If no task_list_id is provided, uses the default configured task list.
-   `search_tasks(query: str, task_list_id: Optional[str] = None, max_results: int = 50)`: Searches for tasks by query text across task titles and descriptions.
-   `search_tasks_by_period(start_date: str, end_date: str, task_list_id: Optional[str] = None, max_results: int = 50)`: Searches for tasks within a specific date period using ISO 8601 format (YYYY-MM-DD).
-   `create_task(title: str, task_list_id: Optional[str] = None, description: Optional[str] = None, due_date: Optional[str] = None, parent_task_id: Optional[str] = None)`: Creates new tasks or sub-tasks with optional description, due date, and parent task for hierarchical structures.
-   `update_task(task_id: str, task_list_id: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None, due_date: Optional[str] = None, status: Optional[str] = None)`: Updates existing task properties with partial update support.
-   `mark_task_completed(task_id: str, task_list_id: Optional[str] = None, completed: bool = True)`: Marks tasks as completed or incomplete, automatically setting completion timestamps.

## Content Search Features

The Google Drive content search functionality supports:

### Supported File Types
- **Google Docs** (native API support)
- **PDF files** (text extraction)
- **Plain text files** (TXT, CSV)
- **Microsoft Word documents** (DOCX)

### Search Options
- **Case-sensitive/insensitive search**
- **Regular expression support**
- **Folder-specific search scope**
- **File type filtering**
- **Configurable result limits**

### Search Results Include
- File metadata (name, ID, creation/modification dates, size)
- Content snippets with highlighted matches
- Match count and positions
- Parent folder information

### Example Usage

#### Google Drive Content Search

```python
# Basic content search
search_drive_by_content("project requirements")

# Case-sensitive search
search_drive_by_content("API", case_sensitive=True)

# Regex search for email patterns
search_drive_by_content(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", use_regex=True)

# Search within specific folder
search_drive_by_content("budget", folder_id="folder123")

# Search specific file types only
search_drive_by_content("report", file_types=["application/pdf", "application/vnd.google-apps.document"])

# Search within a specific file
search_within_file_content("file_id_123", "specific term")
```

#### Gmail Label Management

```python
# List all labels
list_gmail_labels()

# Search for labels containing "work"
search_gmail_labels("work")

# Get details for a specific label
get_gmail_label_details("Label_123")
```

#### Google Tasks Management

```python
# List all available task lists
list_task_lists()

# List tasks from default task list
list_tasks()

# Search for tasks containing "meeting"
search_tasks("meeting")

# Search for tasks due in a specific period
search_tasks_by_period("2024-01-01", "2024-01-31")

# Create a new task
create_task("Review project proposal", description="Review the Q1 project proposal document")

# Create a sub-task
create_task("Prepare presentation", parent_task_id="task123", due_date="2024-01-15")

# Update task description
update_task("task123", description="Updated project proposal review with new requirements")

# Mark task as completed
mark_task_completed("task123", completed=True)
```

## Prerequisites

-   Python 3.10+
-   Docker and Docker Compose (for containerized deployment)
-   A Google Cloud project with the necessary APIs enabled.

## Setup and Configuration

1.  **Google Cloud Credentials**:
    
    **Step 1: Create a Google Cloud Project**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Click the project drop-down at the top of the page and select "New Project".
    *   Enter a project name (e.g., "google-workspace-mcp") and click "Create".
    *   Wait for the project to be created and then select it from the project drop-down.

    **Step 2: Enable Required APIs**
    *   In your new project, navigate to "APIs & Services" > "Library".
    *   Search for and enable the following APIs one by one:
        *   **Google Drive API** - Search for "Google Drive API" and click "Enable"
        *   **Gmail API** - Search for "Gmail API" and click "Enable"
        *   **Google Calendar API** - Search for "Google Calendar API" and click "Enable"
        *   **Google Tasks API** - Search for "Tasks API" and click "Enable"

    **Step 3: Configure OAuth Consent Screen**
    *   Navigate to "APIs & Services" > "OAuth consent screen".
    *   Choose **External** and click "Create".
    *   Fill in the required fields:
        *   **App name**: Google Workspace MCP Server
        *   **User support email**: Your email address
        *   **Developer contact information**: Your email address
    *   Click "SAVE AND CONTINUE".
    *   On the "Scopes" page, click "ADD OR REMOVE SCOPES".
    *   Find and add the following scopes:
        *   `https://www.googleapis.com/auth/drive.readonly` (View files in your Google Drive)
        *   `https://www.googleapis.com/auth/gmail.readonly` (Read all resources and their metadata)
        *   `https://www.googleapis.com/auth/calendar.readonly` (View events on all your calendars)
        *   `https://www.googleapis.com/auth/tasks` (Manage your tasks)
    *   Click "Update", then "SAVE AND CONTINUE".
    *   On the "Test users" page, click "+ ADD USERS".
    *   Add your Google account email address (the account whose Drive, Gmail, and Calendar you'll be accessing).
    *   Click "SAVE AND CONTINUE".

    **Step 4: Create OAuth 2.0 Credentials**
    *   Navigate to "APIs & Services" > "Credentials".
    *   Click "+ CREATE CREDENTIALS" > "OAuth client ID".
    *   For **Application type**, select **Desktop app**.
    *   Give it a name like "Google Workspace MCP Server".
    *   Click "CREATE".
    *   A pop-up will appear with your Client ID and Client Secret. Click **DOWNLOAD JSON**.
    *   Rename the downloaded file to `credentials.json` and save it in the root directory of this project.
    *   **Important**: This file contains sensitive information and should not be shared publicly or committed to version control.

2.  **Local Environment (for development)**:
    *   It is highly recommended to use a virtual environment to manage project dependencies.
        ```bash
        python3 -m venv .venv
        ```
    *   Install the required Python packages:
        ```bash
        ./.venv/bin/pip install -r requirements.txt
        ```

## Configuration Options

### Default Calendar IDs

You can configure default calendar IDs that will be used when no specific calendar is provided. This is useful for setting up commonly used calendars.

**Environment Variable**: `DEFAULT_CALENDAR_IDS`

**Example**:
```bash
export DEFAULT_CALENDAR_IDS="primary,work@company.com,personal@gmail.com"
```

### Content Search Configuration

You can configure content search behavior using environment variables:

**Environment Variables**:
- `MAX_CONTENT_SEARCH_RESULTS`: Maximum number of search results (default: 50)
- `CONTENT_SEARCH_SNIPPET_LENGTH`: Length of search result snippets in characters (default: 200)

**Example**:
```bash
export MAX_CONTENT_SEARCH_RESULTS=100
export CONTENT_SEARCH_SNIPPET_LENGTH=300
```

### Google Tasks Configuration

You can configure Google Tasks behavior using environment variables:

**Environment Variables**:
- `DEFAULT_TASK_LIST_ID`: Default task list ID to use (default: '@default')
- `MAX_TASK_SEARCH_RESULTS`: Maximum number of task search results (default: 100)
- `DEFAULT_TASK_MAX_RESULTS`: Default maximum number of tasks to return when listing (default: 100)

**Example**:
```bash
export DEFAULT_TASK_LIST_ID="@default"
export MAX_TASK_SEARCH_RESULTS=200
export DEFAULT_TASK_MAX_RESULTS=150
```

**In MCP Client Configuration**:
```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "/path/to/python",
      "args": ["server.py"],
      "workingDirectory": "/path/to/project",
      "env": {
        "DEFAULT_CALENDAR_IDS": "primary,work@company.com",
        "MAX_CONTENT_SEARCH_RESULTS": "100",
        "CONTENT_SEARCH_SNIPPET_LENGTH": "300"
      }
    }
  }
}
```

## Running the Server

The server communicates over `stdio`, as is standard for MCP servers. For MCP clients to properly connect, the server should be run directly on the host system.

### Running Locally (Recommended for MCP Clients)

1.  **Start the server**:
    The first time you run the application, it will open a browser window for you to authorize access to your Google account.
    ```bash
    ./.venv/bin/python server.py
    ```
    After successful authorization, a `token.json` file will be created in the root directory to store your OAuth tokens.

### Running with Docker (Alternative)

Docker is primarily useful for deployment scenarios where you want to containerize the application. However, for MCP client integration, running locally is recommended.

1.  **Build and start the container**:
    ```bash
    docker-compose up --build
    ```
    The `docker-compose.yml` configuration ensures that the `credentials.json` file is available to the container and that the `token.json` file is persisted in a Docker volume.

## Connecting to the MCP Server

This server is designed to be used with an MCP host, such as Claude for Desktop or [Gemini CLI](https://github.com/google-gemini/gemini-cli). For proper tool discovery and communication, the server should be run directly on the host system.

### Example MCP Client Configuration

For example, to connect this server to Claude for Desktop or Gemini CLI, you would add the following to your configuration file. Please refer to the official [MCP documentation](https://modelcontextprotocol.io/quickstart/server/#testing-your-server-with-claude-for-desktop) for the location of this file on your system.

#### **Local Server Configuration (Recommended)**

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "/ABSOLUTE/PATH/TO/google-workspace-mcp/.venv/bin/python",
      "args": [
        "server.py"
      ],
      "workingDirectory": "/ABSOLUTE/PATH/TO/google-workspace-mcp",
      "env": {
        "DEFAULT_CALENDAR_IDS": "primary,work@company.com",
        "DEFAULT_TASK_LIST_ID": "@default",
        "MAX_TASK_SEARCH_RESULTS": "100",
        "DEFAULT_TASK_MAX_RESULTS": "100"
      }
    }
  }
}
```

**Important Configuration Notes**:
- **command**: Must point to the Python executable **inside** the virtual environment (`.venv/bin/python`)
- **workingDirectory**: Must be the absolute path to the project root where `server.py` and `credentials.json` are located
- **args**: Uses `server.py` (not the full path) because the working directory is set correctly

**For your system**: The paths above are correct for your current setup. If you move the project, update both the `command` and `workingDirectory` paths accordingly.

#### **Gemini CLI Configuration**

To use this server with [Gemini CLI](https://github.com/google-gemini/gemini-cli), you can configure it in your Gemini CLI settings:

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "/ABSOLUTE/PATH/TO/google-workspace-mcp/.venv/bin/python",
      "args": ["server.py"],
      "workingDirectory": "/ABSOLUTE/PATH/TO/google-workspace-mcp",
      "env": {
        "DEFAULT_CALENDAR_IDS": "primary,work@company.com",
        "DEFAULT_TASK_LIST_ID": "@default",
        "MAX_TASK_SEARCH_RESULTS": "100",
        "DEFAULT_TASK_MAX_RESULTS": "100"
      }
    }
  }
}
```

#### **Docker Server Configuration**

If you prefer to run the server in Docker, you can use the following configuration:

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/ABSOLUTE/PATH/TO/google-workspace-mcp:/app",
        "-w",
        "/app",
        "google-workspace-mcp:latest",
        "python",
        "server.py"
      ],
      "env": {
        "DEFAULT_CALENDAR_IDS": "primary,work@company.com",
        "DEFAULT_TASK_LIST_ID": "@default",
        "MAX_TASK_SEARCH_RESULTS": "100",
        "DEFAULT_TASK_MAX_RESULTS": "100"
      }
    }
  }
}
```

**Prerequisites for Docker Configuration:**
1. **Build the Docker image**:
   ```bash
   docker build -t google-workspace-mcp:latest .
   ```

2. **Ensure credentials.json is in the project root**:
   ```bash
   # Make sure credentials.json is in the project directory
   ls -la credentials.json
   ```

3. **Replace the volume path**: Update `/ABSOLUTE/PATH/TO/google-workspace-mcp` with your actual project path.

**Docker Configuration Notes:**
- The `-i` flag keeps STDIN open for MCP communication
- The `-v` flag mounts your project directory to `/app` in the container
- The `-w /app` sets the working directory in the container
- The `--rm` flag removes the container after it stops
- Environment variables are passed through the `env` section

## Troubleshooting

### Common Issues

#### 1. "No module named 'mcp'" Error
**Problem**: The server can't find the MCP module or other dependencies.

**Solution**: Ensure you're using the Python executable from the virtual environment:
```bash
# Correct way to run the server
.venv/bin/python server.py

# Or activate the virtual environment first
source .venv/bin/activate
python server.py
```

**MCP Configuration Fix**: Make sure the `command` points to the virtual environment Python:
```json
{
  "command": "/ABSOLUTE/PATH/TO/google-workspace-mcp/.venv/bin/python"
}
```

#### 2. "File not found" Errors for server.py or credentials.json
**Problem**: The MCP client can't find the required files.

**Solution**: Ensure the `workingDirectory` is set to the project root:
```json
{
  "workingDirectory": "/ABSOLUTE/PATH/TO/google-workspace-mcp"
}
```

#### 3. OAuth Authentication Issues
**Problem**: The server can't authenticate with Google APIs.

**Solution**: 
1. Ensure `credentials.json` exists in the project root
2. Run the authentication flow manually:
   ```bash
   .venv/bin/python -c "from src.auth import get_credentials; get_credentials()"
   ```
3. Verify `token.json` was created

#### 4. Server Hangs or Doesn't Respond
**Problem**: The server starts but doesn't communicate with the MCP client.

**Solution**: This is normal behavior! The server waits for stdio input from the MCP client. The server should:
- Start successfully (you'll see "Starting MCP server..." in logs)
- Wait for input (no error messages)
- Respond when the MCP client sends requests

### Testing the Configuration

To test if your MCP configuration is correct:

1. **Test the Python executable**:
   ```bash
   /ABSOLUTE/PATH/TO/google-workspace-mcp/.venv/bin/python -c "import mcp; print('✅ MCP module found')"
   ```

2. **Test the server startup**:
   ```bash
   /ABSOLUTE/PATH/TO/google-workspace-mcp/.venv/bin/python /ABSOLUTE/PATH/TO/google-workspace-mcp/server.py
   ```
   You should see "Starting MCP server..." and then the process should wait for input.

3. **Test file accessibility**:
   ```bash
   ls -la /ABSOLUTE/PATH/TO/google-workspace-mcp/server.py
   ls -la /ABSOLUTE/PATH/TO/google-workspace-mcp/credentials.json
   ```

### Connecting with `
