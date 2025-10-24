# FastAPI Auth Products

This project is a FastAPI application that provides user authentication and product management functionalities. It utilizes PostgreSQL as the database and employs PyJWT for handling JSON Web Tokens.

## Project Structure

```
fastapi-auth-products
├── app
│   ├── main.py                # Entry point of the FastAPI application
│   ├── api
│   │   └── v1
│   │       ├── routes
│   │       │   ├── auth.py    # Routes for user authentication (login, registration)
│   │       │   ├── users.py   # Routes for user management (profile retrieval, updates)
│   │       │   └── products.py # Routes for product management (CRUD operations)
│   │       └── dependencies.py # Dependency definitions for authentication and authorization
│   ├── core
│   │   ├── config.py          # Configuration settings (database, secrets)
│   │   └── security.py        # Security functions (password hashing, verification)
│   ├── db
│   │   ├── session.py         # Database session setup for PostgreSQL
│   │   ├── base.py            # Base model for SQLAlchemy
│   │   └── init_db.py        # Database initialization and seeding
│   ├── models
│   │   ├── user.py            # User model definition
│   │   └── product.py         # Product model definition
│   ├── schemas
│   │   ├── user.py            # Pydantic schemas for user validation
│   │   └── product.py         # Pydantic schemas for product validation
│   ├── services
│   │   ├── auth_service.py    # Business logic for authentication (JWT generation)
│   │   └── product_service.py  # Business logic for product management (CRUD)
│   ├── auth
│   │   ├── jwt_handler.py      # JWT token creation and verification
│   │   └── password.py         # Password hashing and checking functions
│   └── utils
│       └── pagination.py       # Utility functions for pagination
├── migrations
│   ├── env.py                 # Alembic migration environment setup
│   └── versions
│       └── .gitkeep           # Keep versions directory in version control
├── tests
│   ├── test_auth.py           # Unit tests for authentication
│   ├── test_users.py          # Unit tests for user management
│   └── test_products.py       # Unit tests for product management
├── requirements.txt            # Project dependencies
├── pyproject.toml             # Project configuration
├── alembic.ini                # Alembic migration configuration
├── docker-compose.yml          # Docker services setup
├── Dockerfile                  # Docker image build instructions
├── .env.example                # Example environment variables
└── README.md                   # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd fastapi-auth-products
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   - Update the database connection settings in `app/core/config.py`.
   - Run the database migrations:
     ```
     alembic upgrade head
     ```

5. **Run the application:**
   ```
   uvicorn app.main:app --reload
   ```

6. **Access the API:**
   Open your browser and navigate to `http://127.0.0.1:8000/api/v1` to see the API documentation.

## Usage

- **Authentication:**
  - Register a new user: `POST /api/v1/auth/register`
  - Login: `POST /api/v1/auth/login`

- **User Management:**
  - Get user info: `GET /api/v1/users/me`
  - Update user profile: `PUT /api/v1/users/me`

- **Product Management:**
  - Create a product: `POST /api/v1/products`
  - Get all products: `GET /api/v1/products`
  - Update a product: `PUT /api/v1/products/{product_id}`
  - Delete a product: `DELETE /api/v1/products/{product_id}`

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.