from fastapi import APIRouter, Depends
from app.internal.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def get_health(service: HealthService = Depends()):
    # Route is responsible for HTTP status mapping and calling service
    result = service.get_system_health()
    return result
