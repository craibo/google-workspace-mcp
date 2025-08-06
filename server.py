#!/usr/bin/env python3
"""
Google Workspace MCP Server
Standalone script for running the MCP server
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
logger.info(f"Added current directory to Python path: {current_dir}")

try:
    from src.mcp_instance import mcp
    logger.info("Successfully imported MCP instance")
    
    # Import the tool modules to ensure the tools are registered
    from src.tools import calendar_tools, drive_tools, gmail_tools
    logger.info("Successfully imported all tool modules")
    
    logger.info("Starting MCP server...")
    
    mcp.run(transport='stdio')
    
except Exception as e:
    logger.error(f"Failed to start server: {e}")
    raise 