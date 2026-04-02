# Roadmap: FinanceBoard

## Overview

FinanceBoard is a role-based finance dashboard backend with JWT authentication, transaction management, and aggregated analytics. The journey builds from infrastructure through authentication to core domain operations, culminating in dashboard analytics that provide the core value.

## Phases

- [ ] **Phase 1: Infrastructure Foundation** - Database setup, async configuration, base models with Decimal types
- [ ] **Phase 2: Authentication & Authorization** - JWT authentication, role-based access control dependencies
- [ ] **Phase 3: Transaction & User Management** - Transaction CRUD, user management, filtering/pagination
- [x] **Phase 4: Dashboard Analytics** - Summary, category breakdown, trends, recent transactions (completed 2026-04-02)

## Phase Details

### Phase 1: Infrastructure Foundation

**Goal**: Database and configuration foundation with correct data types for financial accuracy

**Depends on**: Nothing (first phase)

**Requirements**: None directly (foundation for all other requirements)

**Success Criteria** (what must be TRUE):
1. PostgreSQL schema created via Alembic migrations
2. SQLAlchemy async session configured and working
3. User and Transaction models use Decimal(12, 2) for amounts (not float)
4. Soft delete pattern implemented (is_deleted flag with global query filter)
5. Database indexes created for (user_id, date), (user_id, type), (category)

**Plans**: 3 plans

Plans:
- [ ] 01-01: Set up project structure with FastAPI and dependencies
- [ ] 01-02: Configure SQLAlchemy 2.0 async with PostgreSQL/SQLite
- [ ] 01-03: Create User and Transaction models with correct types and indexes

---

### Phase 2: Authentication & Authorization

**Goal**: Secure JWT-based authentication with role-based access control

**Depends on**: Phase 1

**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, RBAC-01, RBAC-02

**Success Criteria** (what must be TRUE):
1. User can register with email and password (password hashed with Argon2)
2. User can log in and receive JWT access token (30-min expiry)
3. User can refresh access token using refresh token
4. User can view their own profile information
5. VIEWER can access their own transactions (filtered query)
6. VIEWER can access dashboard summary

**Plans**: 4 plans

Plans:
- [x] 02-01-PLAN.md — JWT creation/verification with PyJWT
- [x] 02-02-PLAN.md — Register and login endpoints
- [x] 02-03-PLAN.md — Token refresh endpoint
- [x] 02-04-PLAN.md — Role-based access control dependencies (VIEWER, ANALYST, ADMIN)

---

### Phase 3: Transaction & User Management

**Goal**: Core CRUD operations with role-based access enforcement

**Depends on**: Phase 2

**Requirements**: RBAC-03, RBAC-04, RBAC-05, RBAC-06, RBAC-07, RBAC-08, RBAC-09, RBAC-10, USR-01, USR-02, USR-03, USR-04, TRAN-01, TRAN-02, TRAN-03, TRAN-04, TRAN-05, TRAN-06, TRAN-07

**Success Criteria** (what must be TRUE):
1. User can list their own transactions with filters (type, category, date range), pagination, and sorting
2. User can view a single transaction by ID (ownership verified)
3. ANALYST/ADMIN can list all transactions (not just own)
4. ANALYST/ADMIN can create new transactions
5. ANALYST/ADMIN can update existing transactions
6. ADMIN can soft-delete transactions
7. ADMIN can list all users (paginated)
8. ADMIN can view user by ID
9. ADMIN can update user role and status
10. ADMIN can deactivate users (soft delete)

**Plans**: 4 plans

Plans:
- [ ] 03-01-PLAN.md — Implement Transaction CRUD endpoints with role-based access
- [ ] 03-02-PLAN.md — Add transaction filtering, pagination, and sorting
- [ ] 03-03-PLAN.md — Implement User management endpoints (ADMIN only)
- [ ] 03-04-PLAN.md — Add created_by and updated_by audit fields

---

### Phase 4: Dashboard Analytics

**Goal**: Aggregated financial analytics endpoints for dashboard consumption

**Depends on**: Phase 3

**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04

**Success Criteria** (what must be TRUE):
1. User can view summary (total income, total expenses, net balance)
2. User can view totals grouped by category
3. User can view monthly income/expense trends
4. User can view recent transactions (last N transactions)

**Plans**: 2 plans

Plans:
- [x] 04-01-PLAN.md — Implement dashboard aggregation queries
- [x] 04-02-PLAN.md — Create summary, by-category, trends, and recent endpoints

---

## Progress

**Execution Order:** Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Infrastructure Foundation | 0/3 | Not started | - |
| 2. Authentication & Authorization | 0/4 | Not started | - |
| 3. Transaction & User Management | 0/4 | Not started | - |
| 4. Dashboard Analytics | 2/2 | Complete   | 2026-04-02 |