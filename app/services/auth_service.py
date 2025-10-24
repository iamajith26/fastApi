from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import Customer as User
from app.schemas.user import UserCreate, UserOut, RegistrationMessage
from app.auth.jwt_handler import decode_access_token
from app.auth.password import hash_password, verify_password
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the default password from the .env file
DEFAULT_PSW = os.getenv("DEFAULT_PSW")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_create: UserCreate) -> dict:
        # Hash the password
        hashed_password = pwd_context.hash(DEFAULT_PSW)
    
        if self.db.query(User).filter(User.email == user_create.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(
            name=user_create.name,
            email=user_create.email,
            ph_no=user_create.ph_no,
            pincode=user_create.pincode,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        self.db.commit()
        # self.db.refresh(user)  # not needed since we don't return it
        return RegistrationMessage(detail="User registered successfully").dict()  

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
            return None
        return user

    def get_user(self, user_id: int) -> UserOut:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserOut.from_orm(user)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
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
    except Exception:
        raise credentials_error
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_error
    return user
