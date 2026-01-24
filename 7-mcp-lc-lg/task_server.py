# task_server.py
from mcp.server import FastMCP
from mcp import Resource, Tool
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime

# Simple in-memory task storage
tasks_db = {}

# Initialize MCP Server
server = FastMCP("TaskManager")

# Task data structure


class Task:
    def __init__(self, title: str, description: str = ""):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.completed = False
        self.created_at = datetime.now().isoformat()

# Register task list as a resource


@server.resource("tasks://all")
async def get_all_tasks() -> Resource:
    """Return all tasks as a resource"""
    return Resource(
        uri="tasks://all",
        name="All Tasks",
        mimeType="application/json",
        text=json.dumps([vars(task) for task in tasks_db.values()])
    )


@server.resource("tasks://{task_id}")
async def get_task(task_id: str) -> Resource:
    """Return specific task as a resource"""
    if task_id not in tasks_db:
        raise ValueError(f"Task {task_id} not found")

    task = tasks_db[task_id]
    return Resource(
        uri=f"tasks://{task_id}",
        name=f"Task: {task.title}",
        mimeType="application/json",
        text=json.dumps(vars(task))
    )

# Tool to create new tasks


@server.tool("create_task")
async def create_task(title: str, description: str = "") -> Dict[str, Any]:
    """Create a new task"""
    task = Task(title, description)
    tasks_db[task.id] = task

    return {
        "success": True,
        "task_id": task.id,
        "message": f"Created task: {title}"
    }

# Tool to mark task as complete


@server.tool("complete_task")
async def complete_task(task_id: str) -> Dict[str, Any]:
    """Mark a task as completed"""
    if task_id not in tasks_db:
        return {"success": False, "message": "Task not found"}

    tasks_db[task_id].completed = True
    return {
        "success": True,
        "message": f"Task {task_id} marked as completed"
    }

# Tool to list tasks


@server.tool("list_tasks")
async def list_tasks(completed_only: bool = False) -> Dict[str, Any]:
    """List all tasks or only completed ones"""
    filtered_tasks = []
    for task in tasks_db.values():
        if not completed_only or task.completed:
            filtered_tasks.append(vars(task))

    return {
        "success": True,
        "tasks": filtered_tasks,
        "count": len(filtered_tasks)
    }

# Initialize server with sample data
def initialize_sample_data():
    """Initialize server with sample data"""
    # Add some sample tasks
    sample_tasks = [
        Task("Review MCP documentation", "Go through the MCP protocol specs"),
        Task("Write server example", "Create a practical MCP server example"),
        Task("Test the implementation", "Verify all features work correctly")
    ]

    for task in sample_tasks:
        tasks_db[task.id] = task

    print(f"Task Management MCP Server started with {len(sample_tasks)} sample tasks")

if __name__ == "__main__":
    # Initialize sample data
    initialize_sample_data()
    
    # Run the server using stdio transport (standard for MCP)
    server.run(transport="stdio")
