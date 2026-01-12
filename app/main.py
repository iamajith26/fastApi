from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from app.api.v1.routes import auth, users
from app.dependencies.auth import AuthenticationMiddleware
from app.services.auth_service import get_current_user
from app.models.user import Customer

# Import all models to ensure SQLAlchemy can resolve relationships
import app.models

app = FastAPI(
    title="API Gateway - FastAPI Auth Products",
    description="API Gateway for microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Microservice URLs
PRODUCTS_SERVICE_URL = os.getenv("PRODUCTS_SERVICE_URL", "http://localhost:8001")
ORDERS_SERVICE_URL = os.getenv("ORDERS_SERVICE_URL", "http://localhost:8002")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware only for protected routes
app.add_middleware(AuthenticationMiddleware)

# Include auth and users routes (these stay in the gateway)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])

@app.api_route("/products/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def products_proxy(
    path: str, 
    request: Request, 
    current_user: Customer = Depends(get_current_user)
):
    """Proxy requests to products microservice - Requires authentication"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{PRODUCTS_SERVICE_URL}/products/{path}"
            
            # Forward headers but add user context
            headers = dict(request.headers)
            headers["X-User-ID"] = str(current_user.id)
            headers["X-User-Email"] = current_user.email
            
            if request.method == "GET":
                response = await client.get(url, headers=headers, params=request.query_params)
            elif request.method == "POST":
                body = await request.body()
                response = await client.post(url, headers=headers, content=body)
            elif request.method == "PUT":
                body = await request.body()
                response = await client.put(url, headers=headers, content=body)
            elif request.method == "DELETE":
                response = await client.delete(url, headers=headers)
            
            # Check if the response is successful
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            return response.json()
            
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Products service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with products service: {str(e)}")

@app.api_route("/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def orders_proxy(
    path: str, 
    request: Request, 
    current_user: Customer = Depends(get_current_user)
):
    """Proxy requests to orders microservice - Requires authentication"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{ORDERS_SERVICE_URL}/orders/{path}"
            
            # Forward headers but add user context
            headers = dict(request.headers)
            headers["X-User-ID"] = str(current_user.id)
            headers["X-User-Email"] = current_user.email
            
            if request.method == "GET":
                response = await client.get(url, headers=headers, params=request.query_params)
            elif request.method == "POST":
                body = await request.body()
                response = await client.post(url, headers=headers, content=body)
            elif request.method == "PUT":
                body = await request.body()
                response = await client.put(url, headers=headers, content=body)
            elif request.method == "DELETE":
                response = await client.delete(url, headers=headers)
            
            # Check if the response is successful
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
            return response.json()
            
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Orders service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with orders service: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "API Gateway - FastAPI Microservices"}

@app.get("/health")
async def health_check():
    """Check health of all services"""
    services_health = {}
    
    try:
        async with httpx.AsyncClient() as client:
            # Check products service
            try:
                response = await client.get(f"{PRODUCTS_SERVICE_URL}/health", timeout=5.0)
                services_health["products"] = response.json()
            except:
                services_health["products"] = {"status": "unhealthy"}
            
            # Check orders service
            try:
                response = await client.get(f"{ORDERS_SERVICE_URL}/health", timeout=5.0)
                services_health["orders"] = response.json()
            except:
                services_health["orders"] = {"status": "unhealthy"}
    except:
        pass
    
    return {
        "status": "healthy",
        "service": "api_gateway",
        "services": services_health
    }