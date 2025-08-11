import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
logger.info(f"Added project root to Python path: {project_root}")

try:
    from src.mcp_instance import mcp
    logger.info("Successfully imported MCP instance")
    
    # Import the tool modules to ensure the tools are registered
    from src.tools import calendar_tools, drive_tools, gmail_tools, tasks_tools
    logger.info("Successfully imported all tool modules")
    
    logger.info("Starting MCP server...")
    
    if __name__ == "__main__":
        mcp.run(transport='stdio')
        
except Exception as e:
    logger.error(f"Failed to start server: {e}")
    raise
