# MCP client
# This file will contain the client logic to connect to the MCP server

import json
from typing import Any
from pydantic import AnyUrl
from mcp import types

class MCPClient:
    def __init__(self):
        # Connection and session setup logic will be added in future lectures
        pass

    def session(self):
        """Placeholder method that will return the active MCP session."""
        # return self._session
        pass

    async def list_tools(self):
        """Fetch all available tools from the connected MCP server."""
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(self, tool_name, tool_input):
        """Execute a specific tool on the MCP server."""
        return await self.session().call_tool(
            tool_name,
            tool_input,
        )

    async def read_resource(self, uri: str) -> Any:
        """Read a resource from the MCP server."""
        result = await self.session().read_resource(AnyUrl(uri))

        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)

        return resource.text

    async def list_prompts(self):
        """Fetch all available prompts from the connected MCP server."""
        result = await self.session().list_prompts()
        return result.prompts

    async def get_prompt(self, prompt_name, args):
        """Execute a specific prompt on the MCP server with arguments."""
        result = await self.session().get_prompt(
            prompt_name,
            args,
        )
        return result.messages
