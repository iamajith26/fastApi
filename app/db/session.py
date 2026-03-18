import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from urllib.parse import quote_plus

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

# Get database credentials with URL encoding for special characters
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST') 
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# URL encode the password to handle special characters like @ in Admin@123
if DB_PASSWORD:
    DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)
else:
    raise ValueError("DB_PASSWORD not found in environment variables")

# Construct DATABASE_URL with encoded password
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("One or more required database environment variables are missing")

engine = create_engine(DATABASE_URL, future=True)

# Test connection
try:
    connection = engine.connect()
    print("Database connection successful!")
    connection.close()
except Exception as e:
    print(f"Database connection failed: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()