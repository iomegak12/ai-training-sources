"""Tools endpoint to list available tools."""

from fastapi import APIRouter, Depends
from api.models import ToolInfo, ToolsResponse
from api.dependencies import get_app_state, AppState

router = APIRouter(tags=["Tools"])


@router.get(
    "/tools",
    response_model=ToolsResponse,
    summary="List Available Tools",
    description="Get a list of all available tools that the AI agent can use"
)
async def list_tools(state: AppState = Depends(get_app_state)) -> ToolsResponse:
    """
    List all available tools that the AI agent can use.
    
    Returns:
        ToolsResponse: List of available tools with their descriptions
    """
    return ToolsResponse(
        tools=state.tools_info,
        count=len(state.tools_info)
    )
