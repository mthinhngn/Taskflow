import logging
from datetime import datetime

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CollectorRegistry, REGISTRY
import time

from app.config import get_settings, setup_logging
from app.deps import init_db
from app.routers import auth, tasks, projects, ai
from app.schemas import HealthResponse

settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-assisted task manager with cloud-ready architecture",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
request_count = Counter("taskflow_requests_total", "Total requests", ["method", "endpoint"])
request_duration = Histogram("taskflow_request_duration_seconds", "Request duration", ["method", "endpoint"])


@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Track request metrics."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    request_count.labels(method=request.method, endpoint=request.url.path).inc()
    request_duration.labels(method=request.method, endpoint=request.url.path).observe(duration)

    return response


# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(ai.router)


# Health check endpoints
@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", timestamp=datetime.utcnow())


@app.get("/readyz", response_model=HealthResponse)
async def readiness_check():
    """Readiness check endpoint."""
    return HealthResponse(status="ready", timestamp=datetime.utcnow())


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(REGISTRY)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/healthz",
        "metrics": "/metrics",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
