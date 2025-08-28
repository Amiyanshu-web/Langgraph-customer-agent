#!/usr/bin/env python3
"""
Start the ATLAS MCP Server on port 8001
Usage: python start_atlas_server.py
"""

if __name__ == "__main__":
    from mcp_server.atlas_fastmcp_server import app
    import uvicorn
    
    print("🚀 Starting ATLAS MCP Server on http://localhost:8001")
    print("📡 Handles external system integrations (orders, KB, tickets, notifications)")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    )
