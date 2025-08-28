#!/usr/bin/env python3
"""
Start the COMMON MCP Server on port 8002
Usage: python start_common_server.py
"""

if __name__ == "__main__":
    from mcp_server.common_fastmcp_server import app
    import uvicorn
    
    print("🚀 Starting COMMON MCP Server on http://localhost:8002")
    print("🔧 Handles internal processing (parsing, normalization, calculations)")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8002,
        log_level="info"
    )
