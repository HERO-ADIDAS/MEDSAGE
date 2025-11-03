# ============================================================
# Imports
# ============================================================

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import router as api_router
from dotenv import load_dotenv
import os
import sys

# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()

# ============================================================
# Create FastAPI Application
# ============================================================

app = FastAPI(
    title="MedSage Diagnostic AI Backend",
    description="AI-Powered Medical Diagnostic Assistant with Hospital Finder",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# ============================================================
# Configure CORS Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ============================================================
# Include API Routes
# ============================================================

# ✅ Register API router FIRST (before static files)
app.include_router(api_router, prefix="/api")

# ============================================================
# API Health & Status Endpoints
# ============================================================

@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint - returns API info."""
    return {
        "message": "MedSage API - AI-Powered Diagnostic System",
        "version": "1.0.0",
        "status": "Running",
        "endpoints": {
            "api_docs": "/api/docs",
            "redoc": "/api/redoc",
            "openapi": "/api/openapi.json",
            "health": "/health"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    Used for monitoring and load balancer checks.
    """
    return {
        "status": "healthy",
        "service": "MedSage API",
        "version": "1.0.0",
        "message": "All systems operational"
    }

@app.get("/api-status", tags=["Status"])
async def api_status():
    """
    Detailed API status with available endpoints and features.
    """
    return {
        "status": "running",
        "service": "MedSage Medical Diagnostic System",
        "version": "1.0.0",
        "features": {
            "diagnostic_chat": "AI-powered symptom analysis",
            "report_generation": "PDF report with clinical summary",
            "hospital_finder": "Find nearest medical facilities"
        },
        "endpoints": {
            "patient_info": "POST /api/patient",
            "diagnostic_chat": "POST /api/chat",
            "generate_report": "POST /api/generate_report",
            "nearest_facilities": "POST /api/get_nearest_facilities",
            "available_pincodes": "GET /api/available_pincodes",
            "api_docs": "/api/docs"
        }
    }

# ============================================================
# Static Files (Optional - Frontend)
# ============================================================

# Mount static files AFTER API routes so API takes precedence

static_dir_path = os.path.join(os.path.dirname(__file__), "..", "static")

if os.path.exists(static_dir_path) and os.path.isdir(static_dir_path):
    try:
        app.mount("/", StaticFiles(directory=static_dir_path, html=True), name="static")
        print(f"Static files mounted at: {static_dir_path}")
    except Exception as e:
        print(f"Warning: Could not mount static files: {e}")
else:
    print(f"ℹ️  Info: Static directory not found at '{static_dir_path}'")
    print("   Frontend will be served via separate development server (e.g., npm run dev)")

# ============================================================
# Startup & Shutdown Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Called when FastAPI server starts."""
    print("\n" + "="*60)
    print(" MedSage Server Starting...")
    print("="*60)
    print(f" API Server: http://127.0.0.1:8000")
    print(f" API Docs: http://127.0.0.1:8000/api/docs")
    print(f" ReDoc: http://127.0.0.1:8000/api/redoc")
    print(f"  Health Check: http://127.0.0.1:8000/health")
    print("="*60)
    print("\n Server initialized successfully!\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Called when FastAPI server shuts down."""
    print("\n MedSage Server shutting down...\n")

# ============================================================
# Error Handlers
# ============================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle uncaught exceptions gracefully."""
    print(f" Unhandled exception: {exc}")
    return {
        "error": "Internal Server Error",
        "detail": str(exc),
        "type": type(exc).__name__
    }

# ============================================================
# Run Server (if executed as script)
# ============================================================

if __name__ == "__main__":
    print("\n Starting MedSage Backend Server...\n")
    # Development mode server launch
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
