Here is a step-by-step plan that breaks down the project into manageable parts, from setting up authentication to containerizing the final application.

### **Project Overview**

The goal is to create a secure MCP (Model-Context-Protocol) server that acts as a bridge between a large language model (or any other agent) and Google Workspace services. This server will expose specific tools to interact with Google Drive, Gmail, and Google Calendar in a read-only capacity. We will use official Google Python client libraries to handle the interactions and OAuth 2.0 for secure authentication. Finally, we'll package the server into a Docker container for easy deployment.

### **Development Steps**

Here is the plan we'll follow:

1.  **Project Setup & Authentication**: Configure a Google Cloud project, enable the necessary APIs, and set up OAuth 2.0 credentials. - **COMPLETED**
2.  **Initial Project Scaffolding**: Create the directory structure, `requirements.txt`, and placeholder Python files. - **COMPLETED**
3.  **Tool Definition**: Define the specific functions (tools) our server will provide for Drive, Gmail, and Calendar. - **COMPLETED**
4.  **Google Drive Integration**: Implement the code to search for files and fetch file content from Google Drive. - **COMPLETED**
5.  **Gmail Integration**: Implement the code to search for emails and fetch email details from Gmail. - **COMPLETED**
6.  **Google Calendar Integration**: Implement the code to search for events and fetch event details from Google Calendar. - **COMPLETED**
7.  **MCP Server Implementation (FastAPI)**: Build a simple web server using FastAPI to expose the tools via API endpoints. - **COMPLETED**
8.  **Containerization with Docker**: Create a Dockerfile and docker-compose.yml to build and run the entire application as a container. - **COMPLETED**

### **MCP Refactoring**

The following steps will refactor the project to use the Model Context Protocol.

1.  **Update Dependencies**: Add the `mcp` library to `requirements.txt`. - **COMPLETED**
2.  **Refactor to MCP Server**: Replace the FastAPI implementation with a `FastMCP` server. - **COMPLETED**
3.  **Refactor Tools**: Convert tool functions to `async` and use the `@mcp.tool()` decorator for registration. - **COMPLETED**
4.  **Update Documentation**: Update the `README.md` and containerization files to reflect the new MCP-based approach. - **COMPLETED**

### **Google Calendar Enhancements**

The following steps will enhance the Google Calendar integration with advanced features:

1.  **Calendar Listing**: Add functionality to list all available calendars for the user. - **COMPLETED**
2.  **Configuration Support**: Implement support for configurable default calendar IDs in MCP client configuration. - **COMPLETED**
3.  **Enhanced Event Listing**: Improve event listing with comprehensive filtering options. - **COMPLETED**
4.  **Calendar ID Requirements**: Update existing calendar tools to require calendar IDs for better precision. - **COMPLETED**
5.  **Test Cases**: Add comprehensive test cases for all calendar functions. - **COMPLETED**
6.  **Documentation**: Update README.md with new calendar features and configuration options. - **COMPLETED**

Let's get started with the Google Calendar enhancements!

---

### **Project Setup & Authentication**

Before we write any Python code, we need to set up our Google Cloud project to get the credentials our application will use to authenticate.

#### **Assumptions:**

*   You have a Google account.
*   You have access to the [Google Cloud Console](https://console.cloud.google.com/).

#### **Instructions:**

1.  **Create a New Google Cloud Project**:
    *   Go to the Google Cloud Console.
    *   Click the project drop-down and select "New Project".
    *   Give it a name, like `python-mcp-server`, and create it.
2.  **Enable the Required APIs**:
    *   In your new project, navigate to "APIs & Services" > "Enabled APIs & services".
    *   Click "+ ENABLE APIS AND SERVICES".
    *   Search for and enable the following APIs one by one:
        *   **Google Drive API**
        *   **Gmail API**
        *   **Google Calendar API**
3.  **Configure the OAuth Consent Screen**:
    *   Navigate to "APIs & Services" > "OAuth consent screen".
    *   Choose **External** and click "Create".
    *   Fill in the required fields:
        *   **App name**: Python MCP Server
        *   **User support email**: Your email address.
        *   **Developer contact information**: Your email address.
    *   Click "SAVE AND CONTINUE".
4.  **Define Scopes**:
    *   On the "Scopes" page, click "ADD OR REMOVE SCOPES".
    *   We need to add the minimum required scopes for reading data. Find and add the following:
        *   `.../auth/drive.readonly` (View files in your Google Drive)
        *   `.../auth/gmail.readonly` (Read all resources and their metadata)
        *   `.../auth/calendar.readonly` (View events on all your calendars)
    *   Click "Update", then "SAVE AND CONTINUE".
5.  **Add Test Users**:
    *   On the "Test users" page, click "+ ADD USERS".
    *   Add the Google account email address you will use to test the application. This is the account whose Drive, Gmail, and Calendar you'll be accessing.
    *   Click "SAVE AND CONTINUE".
6.  **Create OAuth 2.0 Credentials**:
    *   Navigate to "APIs & Services" > "Credentials".
    *   Click "+ CREATE CREDENTIALS" > "OAuth client ID".
    *   For **Application type**, select **Desktop app**.
    *   Give it a name, like `MCP Server Desktop Client`.
    *   Click "CREATE".
    *   A pop-up will appear with your Client ID and Client Secret. Click **DOWNLOAD JSON**.
    *   Rename the downloaded file to `credentials.json` and save it in your project directory. This file is secret and should not be shared publicly.

Great! Our Google Cloud project is now configured. In the next step, we'll define the structure of our tools and start writing some Python code.

---

### **Project Blueprint: Python Google Workspace MCP Server**

Here is the full implementation plan with definitions for each function and examples of the JSON objects they will handle. This plan will serve as a complete blueprint for the project without containing the actual implementation logic.

#### **1. Project Structure and Setup**

First, let's define the file structure for our project.

/google-workspace-mcp/
|
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
|
├── /src/
|   ├── __init__.py
|   ├── main.py               # FastAPI server logic
|   ├── auth.py               # Google OAuth handling
|   ├── config.py             # Configuration management
|   |
|   ├── /tools/
|   |   ├── __init__.py
|   |   ├── drive_tools.py      # Google Drive tool functions
|   |   ├── gmail_tools.py      # Gmail tool functions
|   |   ├── calendar_tools.py   # Calendar tool functions
|
├── credentials.json          # Your downloaded Google OAuth credentials
└── token.json                # Will be generated after the first successful login

The `requirements.txt` file will list our Python dependencies:

```plaintext
# requirements.txt
fastapi
uvicorn
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
pydantic
```

#### **2. Authentication (src/auth.py)**

This module will be responsible for handling the OAuth 2.0 flow. It will have one primary function.

*   **Function:** `get_credentials()`
*   **Purpose:** This function will look for a valid `token.json`. If it doesn't exist or is expired, it will use `credentials.json` to initiate the OAuth 2.0 browser-based authorization flow. Upon success, it creates/updates `token.json` and returns the valid credentials object required by the Google API client libraries.
*   **Returns:** A `google.oauth2.credentials.Credentials` object.

#### **3. Configuration Management (src/config.py)**

This module will handle configuration settings, including default calendar IDs.

*   **Function:** `get_default_calendar_ids() -> List[str]`
*   **Purpose:** Retrieves the list of default calendar IDs from the MCP client configuration or environment variables.
*   **Returns:** A list of calendar IDs to use as defaults when no specific calendar is specified.

#### **4. Tool Definitions**

Here we define the interface for each tool our MCP server will expose. Each function will take simple parameters and return a JSON string.

##### **Google Drive Tools (src/tools/drive_tools.py)**

1.  **Function:** `search_drive(query: str) -> str`
    *   **Description:** Searches for files in Google Drive matching the query. The query can include file names, content, or types (e.g., 'project plan type:document').
    *   **Parameters:**
        *   `query`: The search string.
    *   **Returns:** A JSON string representing a list of files.
    *   **Example JSON Output:**
        ```json
        [
          {
            "id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
            "name": "Project Alpha Plan.gdoc",
            "mimeType": "application/vnd.google-apps.document"
          },
          {
            "id": "2bCdEfGhIjKlMnOpQrStUvWxYz",
            "name": "Project Alpha Budget.gsheet",
            "mimeType": "application/vnd.google-apps.spreadsheet"
          }
        ]
        ```

2.  **Function:** `get_drive_file_details(file_id: str) -> str`
    *   **Description:** Fetches the metadata and content of a specific file by its ID. For Google Docs/Sheets/Slides, it exports the content as plain text.
    *   **Parameters:**
        *   `file_id`: The unique ID of the file.
    *   **Returns:** A JSON string with file details.
    *   **Example JSON Output (for a Google Doc):**
        ```json
        {
          "id": "1aBcDeFgHiJkLmNoPqRsTuVwXyZ",
          "name": "Project Alpha Plan.gdoc",
          "mimeType": "application/vnd.google-apps.document",
          "createdTime": "2025-08-01T10:00:00Z",
          "modifiedTime": "2025-08-05T14:30:00Z",
          "content": "Project Alpha Plan\n\n1. Executive Summary...\n2. Goals...\n"
        }
        ```

##### **Gmail Tools (src/tools/gmail_tools.py)**

1.  **Function:** `search_gmail(query: str) -> str`
    *   **Description:** Searches for emails in Gmail matching the query. The query uses Gmail's standard search operators (e.g., 'from:someone@example.com subject:meeting').
    *   **Parameters:**
        *   `query`: The search string.
    *   **Returns:** A JSON string representing a list of email threads.
    *   **Example JSON Output:**
        ```json
        [
          {
            "id": "123456789abcdefg",
            "subject": "Re: Project Meeting",
            "from": "Jane Doe <jane.doe@example.com>",
            "date": "2025-08-05T04:15:00Z"
          }
        ]
        ```

2.  **Function:** `get_gmail_message_details(message_id: str) -> str`
    *   **Description:** Fetches the full details of a specific email message by its ID.
    *   **Parameters:**
        *   `message_id`: The unique ID of the email message.
    *   **Returns:** A JSON string with email details.
    *   **Example JSON Output:**
        ```json
        {
          "id": "123456789abcdefg",
          "subject": "Re: Project Meeting",
          "from": "Jane Doe <jane.doe@example.com>",
          "to": "John Smith <john.smith@example.com>",
          "date": "2025-08-05T04:15:00Z",
          "body": "Hi John,\n\nYes, I am available at that time.\n\nBest,\nJane"
        }
        ```

##### **Enhanced Google Calendar Tools (src/tools/calendar_tools.py)**

1.  **Function:** `list_calendars() -> str`
    *   **Description:** Lists all available calendars for the authenticated user.
    *   **Parameters:** None
    *   **Returns:** A JSON string representing a list of calendars.
    *   **Example JSON Output:**
        ```json
        [
          {
            "id": "primary",
            "summary": "Your Name",
            "description": "Primary calendar",
            "accessRole": "owner"
          },
          {
            "id": "work@company.com",
            "summary": "Work Calendar",
            "description": "Company work calendar",
            "accessRole": "reader"
          }
        ]
        ```

2.  **Function:** `list_calendar_events(calendar_ids: List[str], start_time: str, end_time: str, query: str = None, max_results: int = 100) -> str`
    *   **Description:** Lists all events from specified calendars within a time period, with optional filtering.
    *   **Parameters:**
        *   `calendar_ids`: List of calendar IDs to search (required).
        *   `start_time`: The start of the time window in ISO 8601 format (e.g., '2025-08-01T00:00:00Z').
        *   `end_time`: The end of the time window in ISO 8601 format.
        *   `query`: Optional text to search for in event summaries and descriptions.
        *   `max_results`: Maximum number of events to return (default: 100).
    *   **Returns:** A JSON string representing a list of events.
    *   **Example JSON Output:**
        ```json
        [
          {
            "id": "xyz123456789",
            "summary": "Team Sync",
            "start": "2025-08-06T10:00:00+10:00",
            "end": "2025-08-06T10:30:00+10:00",
            "calendarId": "primary"
          }
        ]
        ```

3.  **Function:** `search_calendar_events(calendar_ids: List[str], query: str, start_time: str, end_time: str) -> str`
    *   **Description:** Searches for calendar events within a specified time range that match a query.
    *   **Parameters:**
        *   `calendar_ids`: List of calendar IDs to search (required).
        *   `query`: The text to search for in event summaries and descriptions.
        *   `start_time`: The start of the time window in ISO 8601 format (e.g., '2025-08-01T00:00:00Z').
        *   `end_time`: The end of the time window in ISO 8601 format.
    *   **Returns:** A JSON string representing a list of events.
    *   **Example JSON Output:**
        ```json
        [
          {
            "id": "xyz123456789",
            "summary": "Team Sync",
            "start": "2025-08-06T10:00:00+10:00",
            "end": "2025-08-06T10:30:00+10:00",
            "calendarId": "primary"
          }
        ]
        ```

4.  **Function:** `get_calendar_event_details(calendar_id: str, event_id: str) -> str`
    *   **Description:** Fetches the full details of a specific calendar event.
    *   **Parameters:**
        *   `calendar_id`: The ID of the calendar containing the event (required).
        *   `event_id`: The unique ID of the event.
    *   **Returns:** A JSON string with event details.
    *   **Example JSON Output:**
        ```json
        {
          "id": "xyz123456789",
          "summary": "Team Sync",
          "description": "Weekly team sync to discuss project progress.",
          "start": "2025-08-06T10:00:00+10:00",
          "end": "2025-08-06T10:30:00+10:00",
          "attendees": [
            {"email": "jane.doe@example.com", "responseStatus": "accepted"},
            {"email": "john.smith@example.com", "responseStatus": "needsAction"}
          ]
        }
        ```

#### **5. MCP Client Configuration Enhancement**

The MCP client configuration will support optional calendar configuration:

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

#### **6. MCP Server (src/main.py)**

This module will use FastAPI to create the web server. It will have a single endpoint to receive tool-call requests.

*   **Endpoint:** `POST /mcp/call`
*   **Purpose:** To act as the single entry point for the agent to call any of the defined tools.
*   **Request Body JSON Structure:**
    ```json
    {
      "tool_name": "search_drive",
      "parameters": {
        "query": "Project Alpha Plan"
      }
    }
    ```
*   **Success Response (Status 200):** The server will execute the corresponding tool function and return its JSON output directly.
*   **Error Response (Status 400 or 500):** If the tool name is invalid, parameters are missing, or an internal error occurs.
    ```json
    {
      "detail": "Tool 'search_drive' requires a 'query' parameter."
    }
    ```

#### **7. Containerization (Dockerfile & docker-compose.yml)**

##### **Dockerfile**

This file will define the steps to build our Python application into a container image.

```dockerfile
# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./src ./src

# Copy credentials (handle with care in production)
COPY credentials.json ./

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the app when the container launches
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

##### **docker-compose.yml**

This file makes it easy to run our containerized application and manage its configuration.

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build: .
    container_name: python-mcp-server
    ports:
      - "8000:8000"
    volumes:
      # Mount a volume to persist the token.json file across container restarts
      - ./token.json:/usr/src/app/token.json
    # In a real production scenario, use Docker secrets for credentials.json
    # For development, we can mount it as a read-only volume.
    volumes:
      - ./credentials.json:/usr/src/app/credentials.json:ro
      - token_data:/usr/src/app/

volumes:
  token_data:
```

*Note: The `docker-compose.yml` is slightly modified to better handle persisting `token.json` using a named volume.*

This completes the full implementation plan. The next logical step would be to start writing the Python code for each module, beginning with `src/auth.py`.
