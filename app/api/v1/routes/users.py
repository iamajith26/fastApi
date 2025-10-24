from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import Customer as User
from sqlalchemy import text
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the default password from the .env file
DEFAULT_PSW = os.getenv("DEFAULT_PSW")

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    # users = (
    #     db.query(User).filter(User.is_active == True)
    #     .order_by(User.id)
    #     .offset(skip)
    #     .limit(limit if limit <= 500 else 500)  # simple upper cap
    #     .all()
    # )
    
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

@router.post("/create_user", response_model=dict)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    # Hash the password
    hashed_password = pwd_context.hash(DEFAULT_PSW)

    # ORM
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
        hashed_password=hashed_password,  # Use the hashed password here
        is_active=True
    )
    db.add(db_user)   
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

    # Raw SQL
    # # Check if the email already exists using raw SQL
    # query_check = text("SELECT id FROM customer WHERE email = :email")
    # existing = db.execute(query_check, {"email": user.email}).fetchone()
    # if existing:
    #     raise HTTPException(status_code=400, detail="Email already registered")

    # # Insert the new user using raw SQL
    # query_insert = text("""
    #     INSERT INTO customer (name, email, ph_no, pincode, hashed_password, is_active)
    #     VALUES (:name, :email, :ph_no, :pincode, :hashed_password, :is_active)
    #     RETURNING id
    # """)
    # result = db.execute(query_insert, {
    #     "name": user.name,
    #     "email": user.email,
    #     "ph_no": user.ph_no,
    #     "pincode": user.pincode,
    #     "hashed_password": hashed_password,
    #     "is_active": True
    # })
    # db.commit()

    # # Fetch the newly created user ID
    # new_user_id = result.fetchone()[0]
    # return {"message": f"User created successfully with ID {new_user_id}"}

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=dict)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return {"message": "User updated successfully"}

@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # Set is_active to False instead of deleting
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return {"message": "User deactivated successfully"}