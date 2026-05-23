
auth.py receives email/password
auth_service.py hashes/verifies password
database.py gives DB session
models/user.py defines user table
schemas/user.py validates request/response
dependencies.py checks JWT token


When the user logs in, this is the full flow:

React/Login Page
   ↓
POST /auth/login
   ↓
FastAPI auth router
   ↓
Database query for user by email
   ↓
bcrypt password verification
   ↓
JWT token creation
   ↓
Token returned to frontend
   ↓
Frontend stores token
   ↓
Future requests send token in Authorization header



Here is the full lifecycle:

User submits login form
        ↓
React sends POST /auth/login
        ↓
FastAPI validates request body with Pydantic
        ↓
FastAPI opens database session using get_db
        ↓
Backend queries users table by email
        ↓
Backend compares password with bcrypt hash
        ↓
If correct, backend creates JWT with user_id + role + expiry
        ↓
Backend returns token to frontend
        ↓
Frontend stores token in localStorage
        ↓
Axios attaches token to future requests
        ↓
Backend verifies token on protected routes
        ↓
Backend extracts user and checks role
        ↓
Endpoint executes only if user is authenticated/authorized

When a user logs in, the React frontend sends email and password to the FastAPI /auth/login endpoint. FastAPI validates the request using Pydantic, opens a SQLAlchemy database session, and looks up the user by email in PostgreSQL. The stored password is a bcrypt hash, so the backend verifies the plain password against that hash. If valid, the backend creates a JWT containing the user id, role, and expiry time, signs it using the secret key, and returns it to the frontend. The frontend stores this token, usually in localStorage for this assignment, and sends it in the Authorization header as a Bearer token for future API calls. Protected FastAPI routes decode and verify this token, fetch the current user from the database, and check their role before allowing access.