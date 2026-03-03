# Create server parameters for stdio connection
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from dotenv import load_dotenv
import os
# For running asyncio
load_dotenv()
# model for agent
model = ChatOpenAI(model="gpt-4o")

# server parameters
server_params = {
    "task-manager": {
        "transport": "sse",
        "url": "http://localhost:8100/sse"
    },
    "remote-file-system": {
        "transport": "sse",
        "url": "http://localhost:8200/sse"
    }
}

# print(server_params)


async def main(query: str):
    client = MultiServerMCPClient(server_params)
    tools = await client.get_tools()
    agent = create_react_agent(model, tools)
    response = await agent.ainvoke({"messages": query})

    return response

query = """
    can you generate a simple task with task manager stating that we're learning MCP, LangChain and LangGraph with Claude, 
    and should be completed automatically. retrieve all tasks and write them into the file named c:\\data\\programmatic-tasks.txt in the file system.
"""

if __name__ == "__main__":
    response = asyncio.run(main(query))
    print('------------')
    print(response)
