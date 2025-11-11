from fastapi import APIRouter
from app.routers.root import router as root_router_base
from app.routers.health import router as health_router


root_router = APIRouter(prefix="")
root_router.include_router(root_router_base)
root_router.include_router(health_router)
# Add your additional routers here
