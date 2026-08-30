from fastapi import APIRouter
from app.api.v1.emails import router as emails_router
from app.api.v1.forensics import router as forensics_router
from app.api.v1.threat import router as threat_router
from app.api.v1.enrichment import router as enrichment_router
from app.api.v1.graph import router as graph_router
from app.api.v1.reports import router as reports_router

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(emails_router)
api_v1_router.include_router(forensics_router)
api_v1_router.include_router(threat_router)
api_v1_router.include_router(enrichment_router)
api_v1_router.include_router(graph_router)
api_v1_router.include_router(reports_router)
