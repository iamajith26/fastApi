from pydantic import BaseModel, EmailStr
from typing import Optional

class RegistrationMessage(BaseModel):
    detail: str

class UserBase(BaseModel):
    name: str
    email: EmailStr
    ph_no: int
    pincode: int

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    hashed_password: Optional[str] = None
    
class LoginRequest(BaseModel):
    email: EmailStr
    hashed_password: str

class UserInDB(UserBase):
    id: int
    
class UserOut(UserInDB):
    class Config:
        orm_mode = True          # Pydantic v1
        from_attributes = True   # Pydantic v2
        
class UserResponse(UserOut):
    pass

class User(UserInDB):
    pass

