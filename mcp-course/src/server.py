from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("DocumentMCP", log_level="ERROR")

# Import tools, resources, and prompts so they get registered with the mcp instance
import src.tools
import src.resources
import src.prompts

if __name__ == "__main__":
    mcp.run()
