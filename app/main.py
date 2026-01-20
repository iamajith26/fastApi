from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from app.api.v1.routes import auth
from app.dependencies.auth import AuthenticationMiddleware
from app.services.auth_service import get_current_user
import logging

app = FastAPI(
    title="E-commerce API Gateway",
    description="Central gateway for e-commerce microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger = logging.getLogger(__name__)

# Microservice URLs
PRODUCTS_SERVICE_URL = os.getenv("PRODUCTS_SERVICE_URL", "http://localhost:8001")
ORDERS_SERVICE_URL = os.getenv("ORDERS_SERVICE_URL", "http://localhost:8002")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8003")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://localhost:8004")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware only for protected routes
app.add_middleware(AuthenticationMiddleware)

# Include only auth routes (users, products, orders now handled by respective services)
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def users_proxy(
    path: str, 
    request: Request, 
    current_user: dict = Depends(get_current_user)
):
    """Proxy requests to users microservice - Requires authentication"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{USERS_SERVICE_URL}/users/{path}"
            
            # Get query parameters
            query_params = dict(request.query_params)
            
            # Forward headers but add user context
            headers = dict(request.headers)
            headers["x-user-id"] = str(current_user["id"])
            
            if request.method == "GET":
                response = await client.get(url, headers=headers, params=query_params)
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
                return {"error": response.text, "status_code": response.status_code}
                
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Users service error: {e}")
        raise HTTPException(status_code=503, detail="Users service unavailable")
    except Exception as e:
        logger.error(f"Error communicating with users service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with users service: {str(e)}")

@app.api_route("/products/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def products_proxy(
    path: str, 
    request: Request, 
    current_user: dict = Depends(get_current_user)
):
    """Proxy requests to products microservice - Requires authentication"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{PRODUCTS_SERVICE_URL}/products/{path}"
            
            # Get query parameters
            query_params = dict(request.query_params)
            
            # Forward headers but add user context
            headers = dict(request.headers)
            headers["x-user-id"] = str(current_user["id"])
            
            if request.method == "GET":
                response = await client.get(url, headers=headers, params=query_params)
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
                return {"error": response.text, "status_code": response.status_code}
                
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Products service error: {e}")
        raise HTTPException(status_code=503, detail="Products service unavailable")
    except Exception as e:
        logger.error(f"Error communicating with products service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with products service: {str(e)}")

@app.api_route("/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def orders_proxy(
    path: str, 
    request: Request, 
    current_user: dict = Depends(get_current_user)
):
    """Proxy requests to orders microservice - Requires authentication"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{ORDERS_SERVICE_URL}/orders/{path}"
            
            # Get query parameters  
            query_params = dict(request.query_params)
            
            # Forward headers but add user context
            headers = dict(request.headers)
            headers["x-user-id"] = str(current_user["id"])
            
            if request.method == "GET":
                response = await client.get(url, headers=headers, params=query_params)
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
                return {"error": response.text, "status_code": response.status_code}
                
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Orders service error: {e}")
        raise HTTPException(status_code=503, detail="Orders service unavailable")
    except Exception as e:
        logger.error(f"Error communicating with orders service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with orders service: {str(e)}")

@app.api_route("/cart/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def cart_proxy(
    path: str, 
    request: Request, 
    current_user: dict = Depends(get_current_user)
):
    """Proxy requests to cart microservice - Mixed authentication (some endpoints public)"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{CART_SERVICE_URL}/cart/{path}"
            
            # Get query parameters  
            query_params = dict(request.query_params)
            
            # Forward headers but add user context
            headers = dict(request.headers)
            headers["x-user-id"] = str(current_user["id"])
            
            if request.method == "GET":
                response = await client.get(url, headers=headers, params=query_params)
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
                return {"error": response.text, "status_code": response.status_code}
                
            return response.json()
            
    except httpx.RequestError as e:
        logger.error(f"Cart service error: {e}")
        raise HTTPException(status_code=503, detail="Cart service unavailable")
    except Exception as e:
        logger.error(f"Error communicating with cart service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error communicating with cart service: {str(e)}")

@app.get("/")
async def read_root():
    return {
        "message": "E-commerce API Gateway",
        "version": "1.0.0",
        "services": {
            "authentication": "/auth",
            "users": "/users",
            "products": "/products", 
            "orders": "/orders",
            "cart": "/cart"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Check health of all services"""
    services_health = {}
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check users service
            try:
                response = await client.get(f"{USERS_SERVICE_URL}/health")
                services_health["users"] = response.json()
            except:
                services_health["users"] = {"status": "unhealthy"}
            
            # Check products service
            try:
                response = await client.get(f"{PRODUCTS_SERVICE_URL}/health")
                services_health["products"] = response.json()
            except:
                services_health["products"] = {"status": "unhealthy"}
            
            # Check orders service
            try:
                response = await client.get(f"{ORDERS_SERVICE_URL}/health")
                services_health["orders"] = response.json()
            except:
                services_health["orders"] = {"status": "unhealthy"}
            
            # Check cart service
            try:
                response = await client.get(f"{CART_SERVICE_URL}/health")
                services_health["cart"] = response.json()
            except:
                services_health["cart"] = {"status": "unhealthy"}
    except:
        pass
    
    return {
        "status": "healthy",
        "service": "api_gateway",
        "services": services_health
    }