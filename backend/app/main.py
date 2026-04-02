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

app.include_router(auth_router, tags=["auth"])

# Business logic routers
from app.routers import transactions, users

app.include_router(transactions.router, tags=["transactions"])
app.include_router(users.router, tags=["users"])

# Dashboard router
from app.routers import dashboard_router

app.include_router(dashboard_router, tags=["dashboard"])