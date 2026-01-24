"""Dependency injection for FastAPI."""

from typing import Dict, Any


# Global state to store the agent and vector database
class AppState:
    """Application state container."""
    agent = None
    vector_db_initialized = False
    tools_info = []


app_state = AppState()


def get_agent():
    """Get the initialized agent instance."""
    if app_state.agent is None:
        raise RuntimeError("Agent not initialized. Server startup may have failed.")
    return app_state.agent


def get_app_state() -> AppState:
    """Get the application state."""
    return app_state
