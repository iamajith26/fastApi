from fastapi import HTTPException, Header, Depends
from typing import Optional
from app.services.auth_service import get_current_user
import logging
import os

logger = logging.getLogger(__name__)

async def validate_gateway_request(
    x_user_id: Optional[str] = Header(None)
):
    """Validate that request comes from authenticated gateway"""
    # Allow direct access for testing/development
    if os.getenv("ALLOW_DIRECT_ACCESS", "false").lower() == "true":
        if not x_user_id:
            logger.warning("Direct access allowed - no gateway headers found")
            return {"user_id": 1}
    
    # Production mode - require gateway headers
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Request must come from authenticated gateway"
        )
    
    logger.info(f"Request from user ID: {x_user_id}")
    return {"user_id": int(x_user_id)}

async def require_admin_role(
    current_user: dict = Depends(get_current_user)
):
    """Validate that the current user has admin role (role_id = 1)"""
    user_role_id = current_user.get("role_id")
    
    if user_role_id != 1:
        logger.warning(f"User {current_user.get('id')} attempted admin action with role_id {user_role_id}")
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin privileges required."
        )
    
    logger.info(f"Admin access granted to user {current_user.get('id')}")
    return current_user