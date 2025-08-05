# Google Workspace MCP Server

This project is a secure MCP (Model-Context-Protocol) server that acts as a bridge between a large language model (or any other agent) and Google Workspace services. It exposes a set of tools to interact with Google Drive, Gmail, and Google Calendar in a read-only capacity.

This server is built using the official [Python MCP SDK](https://modelcontextprotocol.io/quickstart/server) and is ready to be used with any MCP-compatible host, such as Claude for Desktop.

## Features

-   **Google Drive**: Search for files and retrieve file content.
-   **Gmail**: Search for emails and fetch email details.
-   **Google Calendar**: Search for events and get event details.
-   **OAuth 2.0**: Secure authentication using Google's OAuth 2.0 flow.
-   **Dockerized**: Ready for deployment with Docker and Docker Compose.

## Available Tools

This server exposes the following tools to the agent:

### Google Drive

-   `search_drive(query: str)`: Searches for files in Google Drive matching the query.
-   `get_drive_file_details(file_id: str)`: Fetches the metadata and content of a specific file by its ID.

### Gmail

-   `search_gmail(query: str)`: Searches for emails in Gmail matching the query.
-   `get_gmail_message_details(message_id: str)`: Fetches the full details of a specific email message by its ID.

### Google Calendar

-   `search_calendar_events(query: str, start_time: str, end_time: str)`: Searches for calendar events within a specified time range that match a query.
-   `get_calendar_event_details(event_id: str)`: Fetches the full details of a specific calendar event.

## Prerequisites

-   Python 3.10+
-   Docker and Docker Compose (for containerized deployment)
-   A Google Cloud project with the necessary APIs enabled.

## Setup and Configuration

1.  **Google Cloud Credentials**:
    *   Follow the instructions in the [**Service Implementation Plan**](.cursor/rules/google-workspace-mcp.md) to set up your Google Cloud project and download your OAuth 2.0 client credentials.
    *   Rename the downloaded JSON file to `credentials.json` and place it in the root directory of this project. This file is sensitive and should not be committed to version control.

2.  **Local Environment (for development)**:
    *   It is highly recommended to use a virtual environment to manage project dependencies.
        ```bash
        python3 -m venv .venv
        ```
    *   Install the required Python packages:
        ```bash
        ./.venv/bin/pip install -r requirements.txt
        ```

## Running the Server

The server is designed to be run with Docker, which is the recommended approach for both development and production. It communicates over `stdio`, as is standard for MCP servers.

### Running with Docker

1.  **Build and start the container**:
    ```bash
    docker-compose up --build
    ```
    The `docker-compose.yml` configuration ensures that the `credentials.json` file is available to the container and that the `token.json` file is persisted in a Docker volume. The first time you run this, a browser window will open for you to authorize the application.

### Running Locally (for debugging)

You can also run the server locally for easier debugging:

1.  **Start the server**:
    ```bash
    ./.venv/bin/python -m src.server
    ```

## Connecting to the MCP Server

This server is designed to be used with an MCP host, such as Claude for Desktop. To connect, you will need to configure the host to launch the server using `docker-compose`.

### Example MCP Client Configuration

For example, to connect this server to Claude for Desktop, you would add the following to your `claude_desktop_config.json` file. Please refer to the official [MCP documentation](https://modelcontextprotocol.io/quickstart/server/#testing-your-server-with-claude-for-desktop) for the location of this file on your system.

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "docker-compose",
      "args": [
        "up"
      ],
      "workingDirectory": "/ABSOLUTE/PATH/TO/google-workspace-mcp"
    }
  }
}
```

**Note**: You must replace `/ABSOLUTE/PATH/TO/google-workspace-mcp` with the actual absolute path to this project's directory on your machine.

### Connecting with `mcp-remote`

Alternatively, you can use the `mcp-remote` utility to expose the server over HTTP. This is useful for connecting to clients that expect an HTTP endpoint or for remote access.

1.  **Run the server with `mcp-remote`**:
    ```bash
    mcp-remote --port 8000 -- ./venv/bin/python -m src.server
    ```
    This will start the MCP server and make it available at `http://localhost:8000`.

2.  **Configure your MCP client**:
    You can now configure your client to connect to this HTTP endpoint. For example, if your client supports remote server configurations, you would provide it with the URL `http://localhost:8000`.
