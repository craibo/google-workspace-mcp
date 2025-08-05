from src.mcp_instance import mcp
# Import the tool modules to ensure the tools are registered
from src.tools import calendar_tools, drive_tools, gmail_tools

if __name__ == "__main__":
    mcp.run(transport='stdio')
