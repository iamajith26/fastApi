from fastapi import HTTPException, Header
from typing import Optional
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