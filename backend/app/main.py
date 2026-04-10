from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, get_db
from app.api import auth, teams, players, fixtures, matches, standings, admin
from app.services.auth_service import AuthService


# Create FastAPI app
app = FastAPI(
    title="Pickleball League Management System",
    description="A production-ready web application for managing a 10-team Pickleball league",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# PATCH: Fix the broken build_middleware_stack() method in FastAPI
# The bug is in how it unpacks middleware tuples
original_build = app.build_middleware_stack

def fixed_build_middleware_stack():
    """Fixed version that handles Middleware objects properly"""
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.middleware import Middleware as MiddlewareClass
    
    # If there's no user middleware, just return the router
    if not app.user_middleware:
        return app.router
    
    # Start with the router
    app_stack = app.router
    
    # Wrap with user middleware in reverse order
    # Handle both Middleware objects and tuples
    for middleware in reversed(app.user_middleware):
        if isinstance(middleware, MiddlewareClass):
            # It's a Middleware object - extract cls and options
            cls = middleware.cls
            options = middleware.kwargs
        else:
            # It's a tuple
            cls, options = middleware
        
        # Instantiate the middleware
        if isinstance(cls, type) and issubclass(cls, BaseHTTPMiddleware):
            app_stack = cls(app=app_stack, **options)
        else:
            app_stack = cls(app=app_stack, **options)
    
    return app_stack

app.build_middleware_stack = fixed_build_middleware_stack

# Add CORS middleware using the standard approach
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers AFTER creating the app
app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(fixtures.router)
app.include_router(matches.router)
app.include_router(standings.router)
app.include_router(admin.router)


# Define startup event
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


# Define HTTP endpoints
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
