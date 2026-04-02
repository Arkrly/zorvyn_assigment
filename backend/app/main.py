from fastapi import FastAPI

app = FastAPI(
    title="FinanceBoard API",
    version="1.0.0",
    description="Finance Data Processing & Access Control System",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Import routers here for future expansion
from app.auth import router as auth_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

# from app.routers import users, transactions, dashboard
# app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
# app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
# app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])