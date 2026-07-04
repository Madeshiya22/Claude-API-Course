import asyncio
import sys
from config import client
from mcp_client import MCPClient


async def run_chat():
    messages = []

    print("Starting MCP CLI Chatbot. Connecting to FastMCP Server...")

    # Connect to the local server via uv run
    async with MCPClient(command="uv", args=["run", "mcp_server.py"]) as mcp:
        mcp_tools = await mcp.list_tools()
        tools = [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in mcp_tools
        ]
        print(f"Connected! Available tools: {[t.name for t in mcp_tools]}")
        print("Type 'exit' to quit.\n")

        while True:
            try:
                user_input = input("You: ")
            except (KeyboardInterrupt, EOFError):
                break

            if user_input.strip().lower() == "exit":
                break

            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})

            while True:
                response = client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=2048,
                    messages=messages,
                    tools=tools,
                )

                messages.append({"role": "assistant", "content": response.content})

                if response.stop_reason == "tool_use":
                    tool_results = []

                    for block in response.content:
                        if block.type == "tool_use":
                            print(f"\n[Tool Use] Calling {block.name}...")
                            try:
                                result_text = await mcp.call_tool(
                                    block.name, block.input
                                )
                                is_error = False
                            except Exception as e:
                                result_text = f"Error calling tool: {e}"
                                is_error = True

                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": result_text,
                                    "is_error": is_error,
                                }
                            )
                            print(f"[Tool Result] {result_text}")

                    messages.append({"role": "user", "content": tool_results})
                else:
                    for block in response.content:
                        if block.type == "text":
                            print(f"\nClaude: {block.text}\n")
                    break


if __name__ == "__main__":
    asyncio.run(run_chat())
