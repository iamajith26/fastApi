from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import orders
from app.db.session import get_db

# Import all models to ensure SQLAlchemy can resolve relationships
import app.models

app = FastAPI(
    title="Orders Microservice",
    description="Microservice for order management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router, prefix="/orders", tags=["orders"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orders"}