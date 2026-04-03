# FinanceBoard API

FastAPI-based finance data processing and access control system with role-based permissions and analytics.

[![Python version](https://img.shields.io/badge/Python->=3.11-3776AB?style=flat-square&logo=python&logoColor=fff)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=fff)](https://fastapi.tiangolo.com)

FinanceBoard is a RESTful API for managing financial transactions with built-in role-based access control, soft deletes, and analytics endpoints.

> [!TIP]
> Interactive API documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc) when the server is running.

## Features

- **JWT Authentication** — Stateless token-based auth with access and refresh tokens
- **Role-Based Access Control** — Three roles (VIEWER, ANALYST, ADMIN) with granular permissions
- **Transaction Management** — CRUD operations with filtering, pagination, and sorting
- **Analytics Dashboard** — Summary stats, category breakdowns, and monthly trends
- **Soft Deletes** — Data preservation with audit trail support
- **Async Database** — Full async I/O with SQLAlchemy 2.0 and PostgreSQL

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL / SQLite (dev) |
| Auth | JWT + passlib |
| Validation | Pydantic v2 |
| Migrations | Alembic |

## Quick Start

### 1. Clone and Install

```bash
cd backend
cp .env.example .env
# Edit .env and add SECRET_KEY (generate with: openssl rand -hex 32)
pip install -e ".[dev]"
```

### 2. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 3. Run the App

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker (PostgreSQL)

```bash
docker-compose up -d
# Then update DATABASE_URL in .env to use PostgreSQL
alembic upgrade head
```

## Environment Variables

Create `backend/.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | SQLite (dev) or PostgreSQL (prod) connection string |
| `SECRET_KEY` | Yes | JWT signing key (generate with `openssl rand -hex 32`) |
| `ALGORITHM` | No | JWT algorithm (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Access token expiry (default: 30) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | Refresh token expiry (default: 7) |
| `DEBUG` | No | Debug mode (default: false) |

## Deployment

### Render.com (Free Tier)

1. **Create a PostgreSQL database** on Render
   - Go to Dashboard > New > PostgreSQL
   - Note the connection string

2. **Deploy the API**
   - Dashboard > New > Web Service
   - Connect your GitHub repository
   - Build command: `pip install -e .[dev]`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set environment variables**
   - Add all variables from `.env.example`
   - Use the PostgreSQL connection string for `DATABASE_URL`
   - Generate a new `SECRET_KEY` for production

### Railway

1. **Create a Railway project**
   - Add PostgreSQL plugin

2. **Deploy**
   - Connect GitHub repository
   - Set environment variables in Railway dashboard
   - Deploy

### Fly.io

1. **Install flyctl** and authenticate
2. **Create app**: `fly launch`
3. **Add PostgreSQL**: `fly postgres attach`
4. **Deploy**: `fly deploy`

> [!NOTE]
> Update `DATABASE_URL` to use the PostgreSQL connection string provided by your hosting platform.

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Get JWT token |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Current user info |

### Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/transactions` | List (filtered, paginated) |
| POST | `/api/v1/transactions` | Create (ANALYST/ADMIN) |
| GET | `/api/v1/transactions/{id}` | Get by ID |
| PATCH | `/api/v1/transactions/{id}` | Update (ANALYST/ADMIN) |
| DELETE | `/api/v1/transactions/{id}` | Soft delete (ADMIN) |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/summary` | Total income, expenses, balance |
| GET | `/api/v1/dashboard/categories` | Totals by category |
| GET | `/api/v1/dashboard/trends` | Monthly trends |
| GET | `/api/v1/dashboard/recent` | Recent transactions |

### Users (Admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users` | List users |
| GET | `/api/v1/users/{id}` | Get user |
| PATCH | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Deactivate user |

## Role Permissions

| Action | VIEWER | ANALYST | ADMIN |
|--------|:------:|:-------:|:-----:|
| View own transactions | ✓ | ✓ | ✓ |
| View all transactions | | ✓ | ✓ |
| Create transactions | | ✓ | ✓ |
| Update transactions | | ✓ | ✓ |
| Delete transactions | | | ✓ |
| View dashboard | ✓ | ✓ | ✓ |
| Manage users | | | ✓ |

## Data Models

### User
```
id          UUID
email       String (unique)
name        String
role        VIEWER | ANALYST | ADMIN
is_active   Boolean
is_deleted  Boolean (soft delete)
created_at  DateTime
updated_at  DateTime
```

### Transaction
```
id          UUID
user_id     FK → users
type        INCOME | EXPENSE
amount      Decimal(12,2)
category    String
description String (optional)
date        DateTime
is_deleted  Boolean (soft delete)
created_at  DateTime
updated_at  DateTime
```

## Running Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── core/
│   │   ├── config.py        # Settings
│   │   └── security.py      # JWT, password hashing
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   ├── auth/                # Authentication
│   ├── dashboard/           # Analytics
│   └── db/                  # Database session
├── alembic/                 # Migrations
└── tests/                   # Test suite
```

## Design Decisions

- **UUID primary keys** — Avoids ID enumeration, suitable for distributed systems
- **Soft deletes** — Financial data should never be hard-deleted
- **Decimal amounts** — Avoids floating-point precision errors
- **Async throughout** — Consistent non-blocking I/O pattern
- **JWT stateless auth** — Frontend-friendly, scales horizontally
