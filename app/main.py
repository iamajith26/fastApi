from fastapi import FastAPI
from app.api.v1.routes import auth, users, products, orders
from app.dependencies.auth import AuthenticationMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FastAPI Auth Products",
    description="API documentation for user authentication and product management.",
    version="1.0.0",
    docs_url="/docs",         # Swagger UI
    redoc_url="/redoc"        # ReDoc UI
)

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the authentication middleware
app.add_middleware(AuthenticationMiddleware)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    cleaned = []
    for err in exc.errors():
        loc = err.get("loc", [])
        # Extract field name (last string part that's not 'body')
        field_name = None
        for part in reversed(loc):
            if isinstance(part, str) and part != "body":
                field_name = part
                break
        # Build custom message "field_name Field required"
        base_msg = err.get("msg")
        custom_msg = f"{field_name} {base_msg}" if field_name and base_msg else base_msg
        cleaned.append({
            "error": custom_msg,
            "type": err.get("type"),
        })
    return JSONResponse(status_code=422, content={"detail": cleaned})


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application with user authentication and product management!"}