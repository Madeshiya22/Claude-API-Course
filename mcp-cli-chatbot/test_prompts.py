import asyncio
from mcp_client import MCPClient

async def main():
    async with MCPClient(
        command="python",
        args=["mcp_server.py"]
    ) as client:

        prompts = await client.list_prompts()

        print("Available Prompts:\n")

        for prompt in prompts:
            print(prompt.name)

        print("\n-----------------------\n")

        messages = await client.get_prompt(
            "format",
            {
                "doc_id": "report.pdf"
            }
        )

        print(messages)

if __name__ == "__main__":
    asyncio.run(main())
