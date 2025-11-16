#!/bin/bash
# Run the MCP Server

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Set defaults
export MCP_HOST=${MCP_HOST:-"0.0.0.0"}
export MCP_PORT=${MCP_PORT:-8001}
export MCP_LOG_LEVEL=${MCP_LOG_LEVEL:-"INFO"}

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install MCP dependencies if needed
if [ ! -f "mcp_installed" ]; then
    echo "Installing MCP dependencies..."
    pip install -r requirements-mcp.txt
    touch mcp_installed
fi

# Run the server
echo "Starting Orion MCP Server on ${MCP_HOST}:${MCP_PORT}..."
python -m mcp_server.server
