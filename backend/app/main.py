from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, recipients, transactions, dashboard, admin, drills, banking, security_ops

# Create database tables automatically
Base.metadata.create_all(bind=engine)

# Seed default demo user on startup if not exists
from app.core.database import SessionLocal
from app.crud.crud import get_user_by_username, create_user
from app.schemas.schemas import UserCreate

db = SessionLocal()
try:
    if not get_user_by_username(db, "demo"):
        demo_user = UserCreate(
            username="demo",
            email="demo@bank.com",
            password="password123",
            mpin="1234"
        )
        create_user(db, demo_user)
        print("Pre-seeded default demo user created: username='demo', password='password123', mpin='1234'")
except Exception as e:
    print(f"Error seeding default database: {e}")
finally:
    db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-grade AI-Powered Financial Decision Intelligence Platform",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, allow all. Change to specific domain in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(recipients.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(drills.router, prefix=settings.API_V1_STR)
app.include_router(banking.router, prefix=settings.API_V1_STR)
app.include_router(security_ops.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to NIRNAY AI Financial Decision Intelligence API"}
