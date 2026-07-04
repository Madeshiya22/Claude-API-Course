import asyncio
from mcp_client import MCPClient

async def run_tests():
    print("Connecting to MCP Server for Testing...")
    
    async with MCPClient(command="uv", args=["run", "mcp_server.py"]) as mcp:
        tools = await mcp.list_tools()
        print(f"\nAvailable tools: {[t.name for t in tools]}")
        
        # Test 1: Read deposition.md
        print("\n--- Test 1: read_document ---")
        result1 = await mcp.call_tool("read_document", {"name": "deposition.md"})
        print(result1)
        
        # Test 2: Edit deposition.md (Find and Replace)
        print("\n--- Test 2: edit_document ---")
        result2 = await mcp.call_tool(
            "edit_document", 
            {
                "name": "deposition.md",
                "old_str": "Jane Doe",
                "new_str": "Rahul's Updated Doe"
            }
        )
        print(result2)
        
        # Test 3: Read deposition.md again
        print("\n--- Test 3: read_document (Verify) ---")
        result3 = await mcp.call_tool("read_document", {"name": "deposition.md"})
        print(result3)
        
        print("\nTests passed successfully!")

if __name__ == "__main__":
    asyncio.run(run_tests())
