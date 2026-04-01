# Architecture Patterns

**Domain:** Finance Dashboard Backend API

**Researched:** 2026-04-01

## Recommended Architecture

The FinanceBoard backend follows a **layered hexagonal architecture** (also known as ports and adapters) with clear separation between HTTP layer, business logic, and data access. This pattern is ideal for the project because it maintains testability, clear boundaries, and aligns with FastAPI's dependency injection system.

```
┌─────────────────────────────────────────────────────────────────┐
│                        HTTP Layer (FastAPI)                     │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────────┐  │
│  │   Auth   │  │  Users   │  │Transactions│  │  Dashboard    │  │
│  │  Router  │  │  Router  │  │  Router   │  │    Router     │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └───────┬───────┘  │
└───────┼─────────────┼──────────────┼────────────────┼──────────┘
        │             │              │                │
        ▼             ▼              ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer (Business Logic)             │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────────┐  │
│  │  Auth    │  │  User    │  │Transaction│  │   Dashboard   │  │
│  │ Service  │  │ Service  │  │ Service   │  │    Service    │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └───────┬───────┘  │
└───────┼─────────────┼──────────────┼────────────────┼──────────┘
        │             │              │                │
        ▼             ▼              ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Access Layer                          │
│              (SQLAlchemy 2.0 Async + Repositories)              │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Database (PostgreSQL)                       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|----------------|--------------------|
| **Routers** (HTTP layer) | Handle HTTP requests/responses, input validation, authentication checks | Services, Pydantic schemas |
| **Services** (business logic) | Orchestrate operations, enforce business rules, coordinate data access | Models, Repositories, other Services |
| **Models** (SQLAlchemy) | Define database schema, table relationships | Database via session |
| **Schemas** (Pydantic) | Request/response validation, serialization | Routers |
| **Core** (shared infrastructure) | Config, security (JWT), shared dependencies | All layers |
| **DB** (infrastructure) | Session management, migrations | PostgreSQL |

## Data Flow

### Write Operations (Create/Update/Delete Transaction)

```
1. HTTP Request → Router (e.g., POST /transactions)
2. Router validates auth token via dependency (get_current_user)
3. Router calls role check dependency (require_role)
4. Router invokes Service layer: transaction_service.create()
5. Service validates business rules, creates Transaction model instance
6. Service commits to database via async session
7. Service returns result to Router
8. Router serializes via Pydantic schema → JSON Response
```

**Key characteristics:**

- Dependency injection flows downward (routers → services → models)
- Services own business logic; routers are thin
- Database sessions injected via FastAPI dependencies
- Pydantic schemas handle all serialization (input + output)

### Read Operations (Dashboard Analytics)

```
1. HTTP Request → GET /dashboard/summary
2. Router validates auth (get_current_user)
3. Router calls dashboard_service.get_summary()
4. Service builds aggregated queries (SUM, GROUP BY)
5. Service returns structured data
6. Router serializes to DashboardSummary schema → JSON
```

### Authentication Flow

```
1. POST /auth/login with credentials
2. Auth router calls auth_service.authenticate()
3. Service verifies password via passlib
4. Service creates JWT via security.create_access_token()
5. Router returns token + user info
```

## Build Order and Dependencies

The project specifies a clear build order that respects component dependencies:

### Phase 1: Infrastructure Foundation
**Components:** Database, migrations, core config

- Set up PostgreSQL schema via Alembic
- Configure SQLAlchemy async session
- Define base models (User, Transaction)
- Create config loading (pydantic-settings)

**Why first:** All other components depend on database connectivity and configuration.

### Phase 2: Authentication Core
**Components:** Auth router, auth service, security utilities

- Implement JWT creation/verification
- Build login/register endpoints
- Create password hashing

**Why second:** Authentication is a cross-cutting concern required by every other endpoint.

### Phase 3: Core Domain (CRUD)
**Components:** User management, Transaction management

- Build user service + router (ADMIN only)
- Build transaction service + router (ANALYST+)
- Implement role-based access via dependency injection

**Why third:** These represent the primary data operations; dashboard aggregations depend on transactions existing.

### Phase 4: Analytics & Dashboard
**Components:** Dashboard router, dashboard service

- Implement summary aggregations (income, expense, balance)
- Build category-based grouping
- Create trend calculations (monthly)

**Why last:** Dashboard is a read-only view that aggregates existing transaction data.

### Phase 5: Frontend Integration
**Components:** React frontend, API client

- Connect to backend APIs
- Build dashboard visualizations

**Why last:** Frontend depends on stable API contracts from backend.

## Component Dependencies Graph

```
                    ┌─────────────────┐
                    │   Core/Config   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │   Auth   │  │  Models  │  │ Schemas  │
        │ Router   │  │ (SQLAlch)│  │(Pydantic)│
        └────┬─────┘  └────┬─────┘  └──────────┘
             │             │
             ▼             ▼
        ┌──────────┐  ┌──────────┐
        │  Auth    │  │Transaction│
        │ Service  │  │  Model   │
        └────┬─────┘  └────┬─────┘
             │             │
             └──────┬──────┘
                    │
                    ▼
             ┌──────────┐
             │  Service │
             │  Layer   │
             └────┬─────┘
                  │
                  ▼
             ┌──────────┐
             │ Database │
             │(Postgres)│
             └──────────┘
```

## Patterns to Follow

### Pattern 1: Thin Routers, Fat Services

Routers should only handle:

- Request parsing (Pydantic)
- Auth dependency injection
- Response serialization
- HTTP-specific concerns (status codes, headers)

Services handle all business logic:

- Validation beyond schema (business rules)
- Multiple model operations
- Transaction coordination

**Example:**

```python
# Router (thin)
@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    data: TransactionCreate,
    current_user: User = Depends(require_role(Role.ANALYST, Role.ADMIN)),
    service: TransactionService = Depends(),
):
    return await service.create(data, current_user.id)

# Service (fat)
class TransactionService:
    async def create(self, data: TransactionCreate, user_id: UUID) -> Transaction:
        # Business logic here: validation, category normalization, etc.
        # Database operations
        return transaction
```

### Pattern 2: Dependency Injection for Reusability

FastAPI's dependency injection enables:

- Easy testing (mock dependencies)
- Shared functionality across routers
- Clear contract between layers

**Example from project:**

```python
# core/dependencies.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    # Verify JWT, fetch user from DB
    return user

def require_role(*roles: Role):
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403)
        return user
    return role_checker
```

### Pattern 3: Async Throughout

The project uses async SQLAlchemy consistently:

- All service methods are `async`
- All database operations use `await`
- Uvicorn runs with async workers

This ensures non-blocking I/O, critical for dashboard APIs that may run multiple aggregations.

### Pattern 4: Schema-Driven Validation

Pydantic v2 handles:

- Request body validation
- Response serialization
- OpenAPI schema generation
- Nested object handling

**Why important for finance:**

- Decimal precision for amounts (no float)
- Date validation
- Enum enforcement (INCOME/EXPENSE, roles)

### Pattern 5: Soft Deletes for Audit

Transactions use `is_deleted` flag rather than hard deletes:

- Preserves audit trail
-符合财务数据合规要求 (finance data compliance)
- Can be toggled for recovery

## Anti-Patterns to Avoid

### Anti-Pattern 1: Business Logic in Routers

**Bad:**

```python
@router.post("/transactions")
async def create_transaction(data: TransactionCreate, user: User = Depends(get_current_user)):
    # BAD: Business logic in router
    if user.role not in [Role.ANALYST, Role.ADMIN]:
        raise HTTPException(403)
    transaction = Transaction(**data.model_dump(), user_id=user.id)
    db.add(transaction)
    await db.commit()  # BAD: Direct DB access in router
```

**Good:** Move to service layer; use dependency injection.

### Anti-Pattern 2: Synchronous DB Calls in Async Endpoints

**Bad:**

```python
# Using sync SQLAlchemy in async endpoint
def get_user(db: Session, user_id: int):
    return db.query(User).get(user_id)
```

**Good:** Use async SQLAlchemy (`async_sessionmaker`, `AsyncSession`).

### Anti-Pattern 3: Hardcoded Configuration

**Bad:**

```python
SECRET_KEY = "hardcoded-secret"  # Bad: Exposed in code
```

**Good:** Use pydantic-settings for environment-based config.

### Anti-Pattern 4: Missing Transaction Boundaries

**Bad:**

```python
async def transfer_funds(from_id, to_id, amount):
    # Missing: No transaction wrapper
    subtract_balance(from_id, amount)
    add_balance(to_id, amount)
```

**Good:** Use DB transactions (savepoints) for atomic operations; but for this project, single-record operations make explicit transactions less critical.

## Scalability Considerations

| Concern | At 100 Users | At 10K Users | At 1M Users |
|---------|--------------|--------------|-------------|
| **Database** | Single PostgreSQL instance | Read replicas for queries | Sharding by tenant/user |
| **Caching** | None needed | Redis for dashboard aggregations | Redis + CDN for static data |
| **API Rate Limiting** | Per-user via dependency | Redis-backed rate limiter | Distributed rate limiting |
| **Dashboard Queries** | Direct SQL aggregation | Materialized views | Pre-computed analytics tables |
| **Session Management** | JWT (stateless) | JWT + Redis token blacklist | Distributed JWT validation |

### Specific Recommendations for This Project

**Current scope (MVP):**

- Single PostgreSQL instance is sufficient
- No caching layer needed initially (dashboard queries are simple aggregations)
- JWT stateless auth scales without session storage
- Dashboard aggregations can be computed live with SQL (PostgreSQL handles sub-second for typical data sizes)

**Future considerations (out of scope, noted for architecture):**

- Add Redis for caching expensive dashboard calculations
- Consider materialized views for trend data if query performance degrades
- Add read replicas if write latency becomes an issue

## Data Flow Summary

| Operation | Flow Direction | Notes |
|-----------|----------------|-------|
| Auth (login/register) | HTTP → Router → Service → Security → DB | Creates JWT token |
| Protected request | HTTP → Dependency (auth) → Router → Service → DB | Token validated per request |
| Transaction CRUD | HTTP → Router → Service → Model → DB | Enforces role permissions |
| Dashboard read | HTTP → Router → Service → DB (aggregations) | Returns computed summaries |
| Database sessions | Injected via `get_db` dependency | Request-scoped lifecycle |

## Sources

- FastAPI Documentation: Bigger Applications (APIRouter patterns) — https://fastapi.tiangolo.com/tutorial/bigger-applications/
- FastAPI Tutorial: SQL (Relational) Databases — https://fastapi.tiangolo.com/tutorial/sql-databases/
- FastAPI Tutorial: Security (OAuth2 with JWT) — https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- Project Specification (PS.md) — Architecture and stack defined by project requirements