from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import users
from app.db.session import get_db
from typing import Optional
import logging
import os

# Import all models to ensure SQLAlchemy can resolve relationships
import app.models

app = FastAPI(
    title="Users Microservice",
    description="Microservice for user management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def validate_gateway_request(
    x_user_id: Optional[str] = Header(None),
    x_user_email: Optional[str] = Header(None)
):
    """Validate that request comes from authenticated gateway"""
    # Allow direct access for testing/development
    if os.getenv("ALLOW_DIRECT_ACCESS", "false").lower() == "true":
        if not x_user_id or not x_user_email:
            logger.warning("Direct access allowed - no gateway headers found")
            return {"user_id": "1", "user_email": "test@example.com"}
    
    # Production mode - require gateway headers
    if not x_user_id or not x_user_email:
        raise HTTPException(
            status_code=401,
            detail="Request must come from authenticated gateway"
        )
    
    logger.info(f"Users request from user: {x_user_email} (ID: {x_user_id})")
    return {"user_id": x_user_id, "user_email": x_user_email}

# Apply authentication dependency to users routes
app.include_router(
    users.router, 
    prefix="/users", 
    tags=["users"],
    dependencies=[Depends(validate_gateway_request)]
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "users"}