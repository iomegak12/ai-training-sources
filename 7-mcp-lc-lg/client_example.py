# client_example.py
from mcp import MCPClient
import asyncio


async def main():
    # Connect to the task server
    client = MCPClient("http://localhost:8000")
    await client.connect()

    # List available resources
    resources = await client.list_resources()
    print("Available resources:", resources)

    # Use tools to interact with tasks
    result = await client.call_tool("create_task", {
        "title": "New task from client",
        "description": "This task was created via MCP client"
    })
    print("Created task:", result)

    # List all tasks
    tasks = await client.call_tool("list_tasks")
    print("All tasks:", tasks)

    # Get tasks as a resource
    all_tasks_resource = await client.get_resource("tasks://all")
    print("Tasks resource:", all_tasks_resource.text)

if __name__ == "__main__":
    asyncio.run(main())
