import asyncio
from fastmcp import Client


async def main():
    async with Client("http://127.0.0.1:8002/mcp") as client:

        tools = await client.list_tools()

        for tool in tools:
            print(tool.name)


asyncio.run(main())