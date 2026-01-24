"""Health check endpoint."""

from fastapi import APIRouter, Depends
from api.models import HealthResponse
from api.dependencies import get_app_state, AppState
from config.settings import settings

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API service"
)
async def health_check(state: AppState = Depends(get_app_state)) -> HealthResponse:
    """
    Health check endpoint to verify the service is running.
    
    Returns:
        HealthResponse: Current health status of the service
    """
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        vector_db_initialized=state.vector_db_initialized
    )
