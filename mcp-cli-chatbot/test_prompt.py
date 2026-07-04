import asyncio
from mcp_client import MCPClient

async def main():
    async with MCPClient(
        command="python",
        args=["mcp_server.py"]
    ) as client:
        
        # Test 1: List Prompts
        print("===== List Prompts Test =====")
        prompts = await client.session.list_prompts()
        print("Available Prompts:\n")
        for p in prompts.prompts:
            print("-", p.name)

        print("\n===== Fetch Prompt Test =====")
        # Test 2: Fetch Prompt
        result = await client.session.get_prompt(
            "format",
            {
                "doc_id": "report.pdf"
            }
        )
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
