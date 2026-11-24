from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.s3 import ensure_buckets_exist
from backend.app.core.redis import get_redis_client, redis_client

# Import Domain Routers
from backend.app.modules.auth.router import router as auth_router
from backend.app.modules.students.router import router as students_router
from backend.app.modules.drives.router import router as drives_router
from backend.app.modules.tpo.router import router as tpo_router
from backend.app.modules.analytics.router import router as analytics_router
from backend.app.modules.ml.router import router as ml_router
from backend.app.modules.admin.router import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure MinIO buckets
    ensure_buckets_exist()
    # Ping Redis
    try:
        r = await get_redis_client()
        await r.ping()
        print("[Startup] Connected to Redis successfully.")
    except Exception as e:
        print(f"[Startup Warning] Could not connect to Redis: {e}")
        
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()
        print("[Shutdown] Closed Redis connection.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Production-grade Student Placement Analytics & Career Intelligence Platform API",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Domain Routers under /api/v1
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(students_router, prefix=settings.API_V1_STR)
app.include_router(drives_router, prefix=settings.API_V1_STR)
app.include_router(tpo_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(ml_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Student Placement Analytics & Career Intelligence Platform API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }
