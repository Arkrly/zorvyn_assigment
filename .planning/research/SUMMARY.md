# Project Research Summary

**Project:** FinanceBoard
**Domain:** Finance Dashboard Backend API
**Researched:** 2026-04-01
**Confidence:** HIGH

## Executive Summary

FinanceBoard is a **role-based finance data processing and access control system** providing transaction management, dashboard analytics, and user administration with JWT authentication. Research confirms the project follows industry best practices with FastAPI + SQLAlchemy 2.0 async architecture, Pydantic v2 validation, and PostgreSQL for financial data integrity.

The recommended stack uses **FastAPI 0.115+**, **SQLAlchemy 2.0 with asyncpg**, and **PyJWT + pwdlib** (updated from the original PS.md which used outdated python-jose/passlib). The architecture implements a layered hexagonal pattern with thin routers and fat services, enabling testability and clear component boundaries.

Key risks center on four critical pitfalls: **access control bypass** (VIEWER/ANALYST role distinction), **float instead of Decimal** for financial amounts, **missing audit trail**, and **JWT security vulnerabilities**. All can be mitigated through explicit ownership checks, proper type usage, audit field implementation, and token hardening. The current PS.md scope covers all table stakes features adequately—CSV export and audit logging should be prioritized in Phase 2.

## Key Findings

### Recommended Stack

The research identified a modern Python async stack aligned with FastAPI's 2025 official recommendations.

**Core technologies:**
- **Python 3.11+** — Full async support, modern typing features
- **FastAPI 0.115+** — Native async, automatic OpenAPI, dependency injection for RBAC
- **Pydantic v2.x** — 40% fewer bugs, Rust-powered performance, integrated with FastAPI
- **PostgreSQL 15+** — ACID compliance for financial data integrity
- **SQLAlchemy 2.0 + asyncpg** — 5x faster than sync alternatives; async throughout
- **PyJWT + pwdlib (Argon2)** — Updated from PS.md; now the official FastAPI recommendation

All versions verified against official documentation (April 2026). Full installation commands and alternatives considered documented in STACK.md.

### Expected Features

**Must have (table stakes):**
- User Registration & Login (JWT) — Foundational authentication
- Role-Based Access Control (VIEWER/ANALYST/ADMIN) — Core security model
- Transaction CRUD + Filtering + Pagination — Core data operations
- Dashboard endpoints (summary, by-category, trends, recent) — Core value
- Soft Delete — Financial data should never be hard-deleted
- Decimal amounts — Critical for financial accuracy (not float)

**Should have (competitive):**
- Export to CSV — High-value user request, medium complexity
- Audit Log — Compliance requirement for financial systems
- API Rate Limiting — Prevents abuse, FastAPI has built-in middleware

**Defer (v2+):**
- Multi-Tenancy — Requires architectural change (B2B feature)
- PDF Export, Webhooks, Budget Tracking, Forecasting — All out of current scope

Feature dependencies are straightforward: Auth → RBAC → Transactions → Dashboard. Full breakdown in FEATURES.md.

### Architecture Approach

The project follows **layered hexagonal architecture** with clear separation:

| Component | Responsibility |
|-----------|----------------|
| **Routers** (HTTP layer) | Handle HTTP requests, input validation, auth checks |
| **Services** (business logic) | Orchestrate operations, enforce business rules |
| **Models** (SQLAlchemy) | Define database schema, table relationships |
| **Schemas** (Pydantic) | Request/response validation, serialization |
| **Core** (shared) | Config, security (JWT), dependencies |

**Key patterns to follow:**
- Thin Routers, Fat Services — routers only handle HTTP concerns
- Dependency Injection — FastAPI's system for testability and reusability
- Async Throughout — All service methods and DB operations are async
- Schema-Driven Validation — Pydantic handles all serialization

Build order: Infrastructure Foundation → Authentication Core → Core Domain (CRUD) → Analytics & Dashboard. Full patterns documented in ARCHITECTURE.md.

### Critical Pitfalls

1. **Access Control Bypass** — VIEWER can only see own transactions, ANALYST can see all. Must implement ownership verification in service layer for every sensitive operation.

2. **Float Instead of Decimal** — PS.md uses Decimal(12, 2) which is correct. Verify implementation never mixes Decimal with float in calculations.

3. **Missing Audit Trail** — Add created_by and updated_by fields to Transaction model; create audit_log table for compliance.

4. **JWT Security Vulnerabilities** — Use strong SECRET_KEY from environment, validate algorithm explicitly, set expiration (PS.md uses 30 min which is good).

5. **Soft Delete Not Applied Consistently** — Use SQLAlchemy where clause to filter is_deleted=False by default; verify all queries respect this.

Full pitfall analysis in PITFALLS.md with warning signs and prevention strategies.

## Implications for Roadmap

Based on research, the suggested phase structure aligns with the build order defined in ARCHITECTURE.md while addressing critical pitfalls early.

### Phase 1: Infrastructure Foundation
**Rationale:** All other components depend on database connectivity and configuration. Must establish correct data types from the start.

**Delivers:**
- PostgreSQL schema via Alembic
- SQLAlchemy async session configuration
- Base models (User, Transaction) with correct Decimal types
- pydantic-settings config loading

**Addresses:**
- Pitfall: Float vs Decimal — Verify Decimal(12, 2) implementation
- Pitfall: Soft Delete — Global query filter from start
- Pitfall: Date/Time — UTC storage with timezone handling
- Pitfall: Performance at scale — Add indexes: (user_id, date), (user_id, type), (category)

**Research Flag:** Low — Standard SQLAlchemy patterns, well-documented

### Phase 2: Authentication & Authorization
**Rationale:** Authentication is a cross-cutting concern required by every other endpoint. Must implement RBAC correctly before building protected resources.

**Delivers:**
- JWT creation/verification with PyJWT
- Login/register endpoints
- Password hashing with pwdlib (Argon2)
- Role-based dependency injection (require_role)

**Addresses:**
- Pitfall: Access Control Bypass — Explicit ownership checks in service layer
- Pitfall: JWT Security — Strong secrets, algorithm validation, constant-time comparison
- Pitfall: Error Message Leaks — Custom exception handlers
- Pitfall: Missing Rate Limiting — FastAPI middleware
- Feature: Rate Limiting (should-have)

**Research Flag:** Medium — RBAC patterns well-documented but critical; verify implementation against PS.md role definitions

### Phase 3: Core Domain (Transactions)
**Rationale:** Primary data operations; dashboard aggregations depend on transactions existing.

**Delivers:**
- User management endpoints (ADMIN only)
- Transaction CRUD endpoints (ANALYST+)
- Role-based access enforcement
- Transaction filtering and pagination

**Addresses:**
- Pitfall: Input Validation — Pydantic constraints (ge=0 for amount), Enum for type
- Pitfall: Missing Audit Trail — created_by and updated_by fields
- Pitfall: Soft Delete Consistency — Integration tests for deleted records
- Feature: Transaction management (table stakes)

**Research Flag:** Low — Standard CRUD patterns

### Phase 4: Analytics & Dashboard
**Rationale:** Read-only view aggregating existing transaction data; final backend phase.

**Delivers:**
- Dashboard summary (total income, expenses, balance)
- Dashboard by category
- Dashboard trends (monthly)
- Recent transactions endpoint

**Addresses:**
- Pitfall: Performance at scale — Query optimization, caching strategy
- Pitfall: Race Conditions — Proper transaction isolation
- Feature: Dashboard endpoints (table stakes)

**Research Flag:** Low — Standard aggregation patterns

### Phase 5: Production Hardening
**Rationale:** Required for production deployment; adds compliance and security.

**Delivers:**
- Audit log table and logging
- CSV export endpoint
- Refresh token rotation (optional, per PS.md future improvements)

**Addresses:**
- Pitfall: Missing Audit Trail — Full audit log implementation
- Feature: Export CSV (should-have)
- Feature: Refresh Token Rotation (differentiator)

**Research Flag:** Medium — Audit logging patterns vary by compliance requirements

### Phase Ordering Rationale

- **Database first** — Correct types (Decimal) and indexes must be established early
- **Auth before CRUD** — Every endpoint requires authentication and authorization
- **CRUD before Dashboard** — Dashboard aggregates transaction data
- **Dashboard before hardening** — Core value delivered before polish
- **Pitfalls addressed in relevant phases** — Access control in Phase 2, soft delete verification in Phase 1/3, audit trail in Phase 5

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Auth):** RBAC implementation details — verify VIEWER vs ANALYST permission boundaries match PS.md spec
- **Phase 5 (Hardening):** Audit log schema — compliance requirements may vary; document what's needed for target use case

Phases with standard patterns (skip research-phase):
- **Phase 1:** SQLAlchemy async patterns well-documented
- **Phase 3:** Standard CRUD patterns
- **Phase 4:** SQL aggregation patterns

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified against FastAPI official docs (April 2026); updated from PS.md recommendations |
| Features | HIGH | Based on PS.md scope and industry standards for finance dashboards |
| Architecture | HIGH | Layered hexagonal pattern well-established; build order logical |
| Pitfalls | HIGH | Critical pitfalls well-documented (OWASP, financial compliance) |

**Overall confidence:** HIGH

### Gaps to Address

- **Multi-tenancy:** Current architecture is single-tenant; if B2B needed later, significant refactor required
- **CSV export complexity:** Assumed medium complexity but depends on data volume; validate during Phase 5 planning
- **Audit log detail level:** Compliance requirements vary (SOX, PCI-DSS); document what's needed for target use case

## Sources

### Primary (HIGH confidence)
- FastAPI Official Docs — https://fastapi.tiangolo.com/
- FastAPI OAuth2 JWT Tutorial — https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- SQLAlchemy 2.0 Async Documentation — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Pydantic Documentation — https://docs.pydantic.dev/latest/
- OWASP API Security Top 10 — authorization and rate limiting

### Secondary (HIGH confidence)
- Project Specification (PS.md) — Architecture and stack requirements
- Industry patterns: Mint, YNAB, Personal Capital finance dashboard implementations

### Tertiary (MEDIUM confidence)
- Complexity estimates based on typical FastAPI patterns; actual effort may vary

---

*Research completed: 2026-04-01*
*Ready for roadmap: yes*