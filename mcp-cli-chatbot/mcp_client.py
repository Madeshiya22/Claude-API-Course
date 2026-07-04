import asyncio
import json
from pydantic import AnyUrl
from mcp import types
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

class MCPClient:
    def __init__(self, command: str, args: list[str]):
        self.server_params = StdioServerParameters(command=command, args=args, env=None)
        self.session: ClientSession | None = None
        self._exit_stack = None

    async def __aenter__(self):
        from contextlib import AsyncExitStack
        self._exit_stack = AsyncExitStack()
        
        transport = await self._exit_stack.enter_async_context(stdio_client(self.server_params))
        read, write = transport
        
        self.session = await self._exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._exit_stack:
            await self._exit_stack.aclose()

    async def list_tools(self):
        """Fetch tools from the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool via the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
            
        result = await self.session.call_tool(tool_name, arguments)
        
        texts = []
        for content in result.content:
            if content.type == "text":
                texts.append(content.text)
            else:
                texts.append(str(content))
                
        return "\n".join(texts)

    async def read_resource(self, uri: str):
        result = await self.session.read_resource(AnyUrl(uri))

        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):

            if resource.mimeType == "application/json":
                return json.loads(resource.text)

            return resource.text
        return resource

    async def list_prompts(self) -> list[types.Prompt]:
        result = await self.session.list_prompts()
        return result.prompts

    async def get_prompt(
        self,
        prompt_name: str,
        args: dict[str, str]
    ):
        result = await self.session.get_prompt(prompt_name, args)
        return result.messages


# tset_case
import asyncio

async def main():
    async with MCPClient(command="python", args=["mcp_server.py"]) as client:

        print("Connected Successfully!\n")

        print("===== LIST =====")
        resources = await client.read_resource("docs://documents")
        print(resources)

        print()

        print("===== REPORT =====")
        report = await client.read_resource("docs://documents/report.pdf")
        print(report)

if __name__ == "__main__":
    asyncio.run(main())
    
# test case
async def main():

    async with MCPClient(
        command="python",
        args=["mcp_server.py"]
    ) as client:

        print("Connected Successfully!\n")

        print("===== Test 1 : List Documents =====")

        docs = await client.read_resource("docs://documents")
        print(docs)

        print("\n===== Test 2 : Read report.pdf =====")

        report = await client.read_resource(
            "docs://documents/report.pdf"
        )

        print(report)


if __name__ == "__main__":
    asyncio.run(main())