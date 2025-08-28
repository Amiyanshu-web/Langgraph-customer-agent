from typing import Any, Dict, Tuple
from mcp_server import atlas_fastmcp_server as atlas_server
from mcp_server import common_fastmcp_server as common_server
# Import the MCP servers directly for now - we'll use them as modules
# This is a simpler approach that works with FastMCP

class MCPClientManager:
    """Client for calling FastMCP tools - using direct module access for simplicity."""
    
    def __init__(self):
        self.atlas_app = atlas_server.app if atlas_server else None
        self.common_app = common_server.app if common_server else None
    
    def call_tool(self, server: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the specified MCP server."""
        try:
            server_key = server.upper()
            
            if server_key == "ATLAS" and self.atlas_app:
                app = self.atlas_app
            elif server_key == "COMMON" and self.common_app:
                app = self.common_app
            else:
                return {"error": f"Server {server} not available"}
            
            # Get the tool function directly from the module
            if server_key == "ATLAS" and atlas_server:
                tool_func = getattr(atlas_server, tool_name, None)
            elif server_key == "COMMON" and common_server:
                tool_func = getattr(common_server, tool_name, None)
            else:
                tool_func = None
            
            if tool_func and hasattr(tool_func, 'fn'):
                # Call the FastMCP tool function
                result = tool_func.fn(arguments)
                return result if isinstance(result, dict) else {"result": result}
            else:
                return {"error": f"Tool {tool_name} not found on {server} server"}
                
        except Exception as e:
            print(f"Error calling tool {tool_name} on {server}: {e}")
            return {"error": str(e)}


# Global MCP client manager instance
mcp_manager = MCPClientManager()


def invoke_mcp_tool(server: str, tool_name: str, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """
    Invoke a tool on an MCP server via HTTP.
    
    Args:
        server: Server name ("ATLAS" or "COMMON")
        tool_name: Name of the tool to call
        payload: Arguments to pass to the tool
        
    Returns:
        Tuple of (result_dict, server_name)
    """
    try:
        # print(f"[MCP] Calling {tool_name} on {server} server with payload: {payload}")
        result = mcp_manager.call_tool(server, tool_name, payload)
        # print(f"[MCP] Result from {tool_name}: {result}")
        return result, server
    except Exception as e:
        print(f"MCP call failed for {tool_name} on {server}: {e}")
        return {"error": str(e)}, server
