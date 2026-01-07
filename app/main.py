# CRITICAL: Apply nest_asyncio FIRST before any other imports
# This allows Playwright sync API to work with asyncio
try:
    import nest_asyncio
    nest_asyncio.apply()
except (ImportError, Exception):
    pass  # nest_asyncio not available or already applied

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import resume, status, job_application, job_discovery

app = FastAPI(title="Job Application Bot API", version="1.0.0")

# CORS for Chrome Extension / Web Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for frontend (optional - serve from separate server in production)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Routers
app.include_router(resume.router, prefix="/resume", tags=["Resume"])
app.include_router(status.router, prefix="/status", tags=["Status"])
app.include_router(job_application.router, tags=["Job Application"])
app.include_router(job_discovery.router, tags=["Job Discovery"])

# Serve frontend (if frontend folder exists)
if os.path.exists("frontend"):
    @app.get("/dashboard")
    async def serve_dashboard():
        return FileResponse("frontend/index.html")
    
    # Serve static files (CSS, JS)
    @app.get("/style.css")
    async def serve_css():
        return FileResponse("frontend/style.css", media_type="text/css")
    
    @app.get("/app.js")
    async def serve_js():
        return FileResponse("frontend/app.js", media_type="application/javascript")
    
    @app.get("/config.js")
    async def serve_config():
        return FileResponse("frontend/config.js", media_type="application/javascript")
    
    # Also mount static directory for other files
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def home():
    """
    Home endpoint - redirects to dashboard if frontend exists
    """
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    return {"message": "Job Bot API is running 🚀", "dashboard": "/dashboard"}
