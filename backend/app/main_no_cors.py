#!/usr/bin/env python3
"""
Test FastAPI app without CORS middleware
This helps isolate if the issue is middleware-specific
"""

from fastapi import FastAPI
from app.config import settings
from app.database import init_db, get_db
from app.api import auth, teams, players, fixtures, matches, standings, admin
from app.services.auth_service import AuthService


# Create FastAPI app WITHOUT any middleware
app = FastAPI(
    title="Pickleball League Management System",
    description="A production-ready web application for managing a 10-team Pickleball league",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Include routers
app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(fixtures.router)
app.include_router(matches.router)
app.include_router(standings.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup():
    """Initialize database and create default admin user"""

    # Create tables
    init_db()

    # Create default admin user
    db = next(get_db())
    try:
        AuthService.initialize_admin(
            db,
            username=settings.DEFAULT_ADMIN_USERNAME,
            email=settings.DEFAULT_ADMIN_EMAIL,
            password=settings.DEFAULT_ADMIN_PASSWORD,
        )
        print(f"✔ Default admin user initialized: {settings.DEFAULT_ADMIN_USERNAME}")
    except Exception as e:
        print(f"Admin initialization error: {e}")
    finally:
        db.close()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Pickleball League Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "ok",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# NOTE: CORS functionality is DISABLED in this test version
# This helps identify if the middleware is the root cause of the unpacking error

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "__main__:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
