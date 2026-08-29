from fastapi import APIRouter
from app.api.v1.emails import router as emails_router
from app.api.v1.forensics import router as forensics_router

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(emails_router)
api_v1_router.include_router(forensics_router)
