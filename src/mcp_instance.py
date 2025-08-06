import logging
from mcp.server.fastmcp import FastMCP

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the FastMCP server instance
mcp = FastMCP("google-workspace")
logger.info("Initialized FastMCP server instance: google-workspace")
