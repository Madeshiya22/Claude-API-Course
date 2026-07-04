import asyncio
from mcp_client import MCPClient

async def test_resources():
    async with MCPClient(command="uv", args=["run", "mcp_server.py"]) as mcp:
        print("Connected to MCP Server!")
        
        # Test 1: List Resources
        print("\n--- Test 1: List Resources ---")
        resources = await mcp.session.list_resources()
        for r in resources.resources:
            print(f"- {r.uri}")
            
        # Test 2: List Templates
        print("\n--- Test 2: List Templates ---")
        templates = await mcp.session.list_resource_templates()
        for t in templates.resourceTemplates:
            print(f"- {t.uriTemplate}")
            
        # Test 3: Read Resource
        print("\n--- Test 3: Read docs://documents/report.pdf ---")
        result = await mcp.session.read_resource("docs://documents/report.pdf")
        if isinstance(result.contents, list):
            for content in result.contents:
                print(content.text)
        else:
            print(result.contents)

if __name__ == "__main__":
    asyncio.run(test_resources())
