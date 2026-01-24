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
    "count-r": {
        "transport": "sse",
        "url": "http://localhost:8000/sse"
    },
    "task-manager": {
        "transport": "sse",
        "url": "http://localhost:8003/sse"
    },
    "remote-file-system": {
        "transport": "sse",
        "url": "http://localhost:8004/sse"
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
    i would like to count the number of r characters from the file test.txt which is located in remote file system.
    Dump the output into a file named output-v2.txt in the remote file system.
    And represent above information in the form of a task and create it.
"""

if __name__ == "__main__":
    response = asyncio.run(main(query))
    print('------------')
    print(response)
