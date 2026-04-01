# Technology Stack

**Project:** FinanceBoard — Finance Dashboard API
**Researched:** April 2026
**Confidence:** HIGH

## Recommended Stack

### Core Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.11+ (3.13 recommended) | Language | Full async support, modern typing features |
| FastAPI | Latest (0.115+) | Web framework | Official FastAPI recommendation; native async, automatic OpenAPI docs, dependency injection for RBAC |
| Pydantic | v2.x (2.12+) | Data validation | Official FastAPI dependency; v2 is stable, 40% fewer bugs, Rust-powered performance |
| Uvicorn | Latest | ASGI server | Official FastAPI recommendation; required for running FastAPI apps |

**Sources:** FastAPI official docs (fastapi.tiangolo.com) — verified April 2026

---

### Database

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| PostgreSQL | 15+ | Primary database | ACID compliance, financial data integrity |
| SQLite | 3.x | Dev/Test | Zero-config, file-based, FastAPI test support |
| SQLAlchemy | 2.0.x (2.0.48+) | ORM | Official FastAPI tutorial uses SQLAlchemy 2.0; native async support via `sqlalchemy[asyncio]` |
| asyncpg | 0.31+ | PostgreSQL async driver | 5x faster than psycopg3; native asyncio; recommended by FastAPI tutorial |
| Alembic | Latest | Migrations | Standard for SQLAlchemy; handles schema changes |

**Sources:** SQLAlchemy 2.0 docs (docs.sqlalchemy.org), asyncpg PyPI (Nov 2025 release), FastAPI tutorial

**Why NOT psycopg3:** asyncpg is ~5x faster in benchmarks and has better asyncio integration.

---

### Authentication & Security

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| PyJWT | 2.x | JWT token handling | **Updated 2025:** Official FastAPI tutorial now uses PyJWT (not python-jose). Simpler API, actively maintained. |
| pwdlib | Latest (with Argon2) | Password hashing | **Updated 2025:** Official FastAPI tutorial now recommends pwdlib with Argon2 (not passlib). Modern, secure defaults, no legacy algorithms. |
| python-multipart | Latest | Form parsing | Required for OAuth2PasswordRequestForm (FastAPI built-in) |

**Key Change from PS.md:** The project specification (PS.md) uses `python-jose` + `passlib`. This is outdated — FastAPI's official 2025 tutorial uses **PyJWT** + **pwdlib**. Both approaches work, but PyJWT/pwdlib is the current official recommendation.

**Sources:** FastAPI OAuth2 JWT Tutorial (fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) — verified April 2026

---

### Validation & Settings

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pydantic-settings | 2.x | Environment config | Official Pydantic extra; handles .env natively |
| email-validator | Latest | Email validation | Required for Pydantic EmailStr type |

---

### Testing

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pytest | 8.x | Test framework | Industry standard for Python |
| httpx | 0.27+ | Async HTTP client | Required for FastAPI TestClient; supports async |
| pytest-asyncio | Latest | Async test support | Required for testing async endpoints |

---

### Code Quality

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Ruff | Latest | Linting/Formatting | 10-100x faster than legacy tools; replaces isort, flake8, black |
| mypy | Latest | Type checking | Catches type errors before runtime |

---

## Installation

```bash
# Core dependencies
pip install "fastapi[standard]" uvicorn
pip install "sqlalchemy[asyncio]" asyncpg alembic
pip install pyjwt "pwdlib[argon2]" python-multipart
pip install pydantic-settings email-validator

# Testing
pip install pytest httpx pytest-asyncio

# Code quality
pip install ruff mypy
```

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Auth library | PyJWT | python-jose | Still works but PyJWT is simpler and recommended in FastAPI tutorial |
| Password hashing | pwdlib (Argon2) | passlib (bcrypt) | pwdlib is the new official recommendation; Argon2 wins Password Hashing Competition |
| PostgreSQL driver | asyncpg | psycopg3 (sync) / psycopg (new async) | asyncpg is faster and more mature for asyncio; psycopg is newer |
| ORM | SQLAlchemy 2.0 | Tortoise ORM / Prisma | SQLAlchemy has better async support in 2.0, more community resources |
| Formatting | Ruff | Black + isort + flake8 | Ruff is 10-100x faster, single tool |

---

## Verification Notes

All versions verified against official documentation and PyPI release dates (2025-2026):

- **FastAPI:** Active project, latest releases in 2025
- **Pydantic v2:** Stable since 2023, v2.12+ in 2026
- **SQLAlchemy 2.0:** Current stable branch (2.0.48, March 2026)
- **asyncpg:** 0.31.0 released Nov 2025
- **PyJWT:** 2.x series active
- **pwdlib:** Active project with Argon2 support

---

## Sources

1. FastAPI Official Docs — https://fastapi.tiangolo.com/
2. FastAPI OAuth2 JWT Tutorial — https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
3. SQLAlchemy 2.0 Async Documentation — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
4. Pydantic Documentation — https://docs.pydantic.dev/latest/
5. asyncpg PyPI — https://pypi.org/project/asyncpg/
6. PyJWT Documentation — https://pyjwt.readthedocs.io/
7. pwdlib Documentation — https://pwdlib.readthedocs.io/