# Google Workspace MCP Server

This project is a secure MCP (Model-Context-Protocol) server that acts as a bridge between a large language model (or any other agent) and Google Workspace services. It exposes a set of tools to interact with Google Drive, Gmail, and Google Calendar in a read-only capacity.

This server is built using the official [Python MCP SDK](https://modelcontextprotocol.io/quickstart/server) and is ready to be used with any MCP-compatible host, such as Claude for Desktop.

## Features

-   **Google Drive**: Search for files, retrieve file content, and perform advanced content-based searches across multiple file types.
-   **Gmail**: Search for emails and fetch email details.
-   **Google Calendar**: List calendars, search events, and get event details with enhanced filtering.
-   **OAuth 2.0**: Secure authentication using Google's OAuth 2.0 flow.
-   **Dockerized**: Ready for deployment with Docker and Docker Compose.
-   **Configurable**: Support for default calendar IDs via environment variables.

## Available Tools

This server exposes the following tools to the agent:

### Google Drive

-   `search_drive(query: str)`: Searches for files in Google Drive matching the query.
-   `get_drive_file_details(file_id: str)`: Fetches the metadata and content of a specific file by its ID.
-   `search_drive_by_content(search_term: str, folder_id: Optional[str] = None, file_types: Optional[List[str]] = None, case_sensitive: bool = False, use_regex: bool = False, max_results: Optional[int] = None)`: Searches for files containing specific text content with advanced options.
-   `search_within_file_content(file_id: str, search_term: str, case_sensitive: bool = False, use_regex: bool = False)`: Searches for specific content within a single file.

### Gmail

-   `search_gmail(query: str)`: Searches for emails in Gmail matching the query.
-   `get_gmail_message_details(message_id: str)`: Fetches the full details of a specific email message by its ID.

### Google Calendar

-   `list_calendars()`: Lists all available calendars for the authenticated user.
-   `list_calendar_events(calendar_ids: Optional[List[str]] = None, start_time: str, end_time: str, query: Optional[str] = None, max_results: int = 100)`: Lists all events from specified calendars within a time period, with optional filtering. If no calendar_ids are provided, uses the default configured calendars.
-   `search_calendar_events(calendar_ids: Optional[List[str]] = None, query: str, start_time: str, end_time: str)`: Searches for calendar events within a specified time range that match a query. If no calendar_ids are provided, uses the default configured calendars.
-   `get_calendar_event_details(event_id: str, calendar_id: Optional[str] = None)`: Fetches the full details of a specific calendar event. If no calendar_id is provided, uses the first configured default calendar.

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

This server is designed to be used with an MCP host, such as Claude for Desktop. For proper tool discovery and communication, the server should be run directly on the host system.

### Example MCP Client Configuration

For example, to connect this server to Claude for Desktop, you would add the following to your `claude_desktop_config.json` file. Please refer to the official [MCP documentation](https://modelcontextprotocol.io/quickstart/server/#testing-your-server-with-claude-for-desktop) for the location of this file on your system.

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
        "DEFAULT_CALENDAR_IDS": "primary,work@company.com"
      }
    }
  }
}
```

**Note**: You must replace `/ABSOLUTE/PATH/TO/google-workspace-mcp` with the actual absolute path to this project's directory on your machine.

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
        "DEFAULT_CALENDAR_IDS": "primary,work@company.com"
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

### Connecting with `mcp-remote`

Alternatively, you can use the `mcp-remote` utility to expose the server over HTTP. This is useful for connecting to clients that expect an HTTP endpoint or for remote access.

1.  **Run the server with `mcp-remote`**:
    ```bash
    mcp-remote --port 8000 -- ./.venv/bin/python server.py
    ```
    This will start the MCP server and make it available at `http://localhost:8000`.

2.  **Configure your MCP client**:
    You can now configure your client to connect to this HTTP endpoint. For example, if your client supports remote server configurations, you would provide it with the URL `http://localhost:8000`.
