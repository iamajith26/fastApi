from fastapi import HTTPException, Depends, status, Header
from fastapi.security import OAuth2PasswordBearer
import httpx
from app.schemas.user import UserCreate, RegistrationMessage, LoginRequest
from app.auth.jwt_handler import decode_access_token
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any
import logging

# Load environment variables from .env file
load_dotenv()

# Get the default password from the .env file
DEFAULT_PSW = os.getenv("DEFAULT_PSW")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8003")

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class AuthService:
    def __init__(self, user_id: str = None):
        self.user_id = user_id

    async def register_user(self, user_create: UserCreate) -> dict:
        """Register user via users microservice"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # No x-user-id header needed for registration - this is for new users
                response = await client.post(
                    f"{USERS_SERVICE_URL}/users/create_user",
                    json=user_create.dict()
                )
                
                if response.status_code == 400:
                    raise HTTPException(status_code=400, detail=response.json().get("detail", "Registration failed"))
                elif response.status_code != 200:
                    raise HTTPException(status_code=500, detail="User service error")
                
                return RegistrationMessage(detail="User registered successfully").dict()
                
        except httpx.RequestError as e:
            logger.error(f"Users service error during registration: {e}")
            raise HTTPException(status_code=503, detail="Users service unavailable")

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user via users microservice"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Use the new public authentication endpoint
                response = await client.post(
                    f"{USERS_SERVICE_URL}/users/authenticate",
                    params={"email": email, "password": password}
                )
                
                if response.status_code == 401:
                    logger.info(f"Authentication failed for email: {email}")
                    return None
                elif response.status_code != 200:
                    logger.error(f"Users service error: {response.status_code} - {response.text}")
                    return None
                
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Users service error during authentication: {e}")
            return None

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID via users microservice"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {}
                if self.user_id:
                    headers["x-user-id"] = self.user_id
                
                response = await client.get(
                    f"{USERS_SERVICE_URL}/users/{user_id}",
                    headers=headers
                )
                
                if response.status_code == 404:
                    raise HTTPException(status_code=404, detail="User not found")
                elif response.status_code != 200:
                    raise HTTPException(status_code=500, detail="User service error")
                
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Users service error: {e}")
            raise HTTPException(status_code=503, detail="Users service unavailable")

def get_auth_service(x_user_id: Optional[str] = Header(None)) -> AuthService:
    return AuthService(user_id=x_user_id)

async def get_current_user(token: str = Depends(oauth2_scheme), x_user_id: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Get current user from JWT token without database access"""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_error
        user_id = int(sub)
        
        # Get user from users service
        auth_service = AuthService(user_id=x_user_id)
        user = await auth_service.get_user(user_id)
        
        if not user:
            raise credentials_error
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise credentials_error
