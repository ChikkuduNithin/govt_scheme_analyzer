from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, profile, schemes, documents, query, eligibility, analyze, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(schemes.router, prefix="/schemes", tags=["schemes"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(eligibility.router, prefix="/eligibility", tags=["eligibility"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
