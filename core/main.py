"""
MinimalERP - Core Application Module

Main FastAPI application with all configurations and middleware.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from core.config import settings
from core.database import engine, Base
from core.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from modules.accounting.api import router as accounting_router
from modules.sales.api import router as sales_router
from modules.inventory.api import router as inventory_router
from modules.pos.api import router as pos_router

# Import models to ensure they're registered with SQLAlchemy
from modules.pos.models import (
    POSSession, POSOrder, POSOrderLine, POSPayment,
    POSProduct, POSCategory, POSConfig
)
from modules.sales.models import Customer, SalesOrder, SalesOrderLine
from modules.inventory.models import (
    Product, ProductCategory, StockLocation, StockMove, StockQuant
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics (use try-except to avoid duplicate registration)
try:
    REQUEST_COUNT = Counter('minimalerp_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
    REQUEST_LATENCY = Histogram('minimalerp_request_latency_seconds', 'Request latency', ['method', 'endpoint'])
except ValueError:
    # Metrics already registered, get existing ones
    from prometheus_client import REGISTRY
    REQUEST_COUNT = REGISTRY._names_to_collectors.get('minimalerp_requests_total')
    REQUEST_LATENCY = REGISTRY._names_to_collectors.get('minimalerp_request_latency_seconds')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 MinimalERP starting up...")

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("✅ Database tables created")
    logger.info("✅ MinimalERP is ready!")

    yield

    # Shutdown
    logger.info("👋 MinimalERP shutting down...")
    await engine.dispose()
    logger.info("✅ Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.APP_VERSION,
    description="Murakabe AI - Yapay Zeka Destekli İşletme Yönetim Platformu",
    docs_url=settings.API_DOCS_URL if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom Middleware
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)

app.add_middleware(RequestLoggingMiddleware)


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Doğrulama hatası",
            "errors": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Sunucu hatası oluştu",
            "detail": str(exc) if settings.DEBUG else "Lütfen daha sonra tekrar deneyin"
        }
    )


# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record request metrics"""
    start_time = time.time()

    response = await call_next(request)

    # Record metrics
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    # Add headers
    response.headers["X-Process-Time"] = str(duration)

    return response


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Metrics endpoint
@app.get("/metrics", tags=["System"])
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """API root endpoint"""
    return {
        "message": "Murakabe AI - Yapay Zeka Destekli İşletme Yönetim Platformu",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_DOCS_URL}",
        "modules": {
            "accounting": "Akıllı Muhasebe ve Finans Yönetimi",
            "sales": "AI-Destekli Satış ve CRM",
            "inventory": "AI-Optimize Stok Yönetimi",
            "pos": "Modern Perakende Satış Noktası (POS)"
        }
    }


# Include module routers
# Include routers
app.include_router(accounting_router)
app.include_router(sales_router)
app.include_router(inventory_router)
app.include_router(pos_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "core.main:app",
        host="0.0.0.0",
        port=5252,
        reload=settings.AUTO_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
