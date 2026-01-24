from agent import agent_executor
from langchain_core.messages import HumanMessage


def query(query: str) -> str:
    if not query:
        raise ValueError("Query string cannot be empty")

    response = agent_executor.invoke({
        "messages": [
            HumanMessage(content=query)
        ]
    })

    return response["messages"][-1].content

