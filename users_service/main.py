from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies.gateway_auth import validate_gateway_request
from users_service.models.user import Customer as User
from sqlalchemy import text
from users_service.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from passlib.context import CryptContext
from dotenv import load_dotenv
from typing import Optional, List
from app.dependencies.gateway_auth import require_admin_role
import logging
import os

# Load environment variables from .env file
load_dotenv()

# Get the default password from the .env file
DEFAULT_PSW = os.getenv("DEFAULT_PSW")

app = FastAPI(
    title="Users Microservice",
    description="Microservice for user management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Users Routes - moved from main app
@app.get("/users/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user_context: dict = Depends(validate_gateway_request),
    db: Session = Depends(get_db),
):
    """Get all users with pagination"""
    # Use raw SQL query to fetch users
    query = text("""
        SELECT id, name, email, ph_no, pincode, is_active
        FROM customer
        WHERE is_active = TRUE
        ORDER BY id
        OFFSET :skip
        LIMIT :limit
    """)
    result = db.execute(query, {"skip": skip, "limit": min(limit, 500)}).fetchall()

    # Convert result to list of dictionaries
    users = [
        {
            "id": row.id,
            "name": row.name,
            "email": row.email,
            "ph_no": row.ph_no,
            "pincode": row.pincode,
            "is_active": row.is_active,
        }
        for row in result
    ]
    return users

@app.post("/users/create_user", response_model=dict)
async def create_user(
    user: UserCreate,
    is_admin = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Create a new user - Public endpoint for registration"""
    # Hash the password
    hashed_password = pwd_context.hash(DEFAULT_PSW)

    # Email uniqueness check
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create the user with the hashed password
    db_user = User(
        name=user.name,
        email=user.email,
        ph_no=user.ph_no,
        pincode=user.pincode,
        hashed_password=hashed_password,
        role_id=2,
        is_active=True
    )
    db.add(db_user)   
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    is_admin = Depends(require_admin_role),
    user_context: dict = Depends(validate_gateway_request),
    db: Session = Depends(get_db)
):
    """Get a specific user by ID"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    user: UserUpdate,
    is_admin = Depends(require_admin_role),
    user_context: dict = Depends(validate_gateway_request),
    db: Session = Depends(get_db)
):
    """Update a user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    is_admin = Depends(require_admin_role),
    user_context: dict = Depends(validate_gateway_request),
    db: Session = Depends(get_db)
):
    """Soft delete a user (deactivate)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Set is_active to False instead of deleting
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return {"message": "User deactivated successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "users"}

# Public endpoint for authentication (no x-user-id required)
@app.post("/users/authenticate")
async def authenticate_user_endpoint(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Public endpoint to authenticate user credentials"""
    try:
        # Find user by email
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not pwd_context.verify(password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Return user data (without password)
        return {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "role_id": db_user.role_id,
            "ph_no": db_user.ph_no,
            "pincode": db_user.pincode,
            "is_active": db_user.is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")