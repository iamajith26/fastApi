import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

USERS_SERVICE_URL = "http://users-service"

class UserService:
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user via users microservice"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Method 1: Using query parameters instead of headers
                response = await client.post(
                    f"{USERS_SERVICE_URL}/users/authenticate",
                    params={"email": email, "password": password, "source": "gateway"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Authentication failed with status code {response.status_code}")
                    return None
                
        except httpx.RequestError as e:
            logger.error(f"Users service error during authentication: {e}")
            return None