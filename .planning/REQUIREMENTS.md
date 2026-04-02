# Requirements: FinanceBoard

**Defined:** 2025-04-01
**Core Value:** A secure, role-based API that allows users to manage financial transactions with proper access control and provides aggregated dashboard analytics.

## v1 Requirements

### Authentication (AUTH)

- [ ] **AUTH-01**: User can register with email and password
- [ ] **AUTH-02**: User can log in and receive JWT access token
- [ ] **AUTH-03**: User can refresh access token
- [ ] **AUTH-04**: User can view their own profile information

### Users (USR)

- [ ] **USR-01**: Admin can list all users (paginated)
- [ ] **USR-02**: Admin can view user by ID
- [ ] **USR-03**: Admin can update user role and status
- [ ] **USR-04**: Admin can deactivate user (soft delete)

### Transactions (TRAN)

- [ ] **TRAN-01**: User can list their own transactions (filtered, paginated)
- [ ] **TRAN-02**: ANALYST/ADMIN can list all transactions (filtered, paginated)
- [ ] **TRAN-03**: ANALYST/ADMIN can create a new transaction
- [ ] **TRAN-04**: User can view transaction by ID
- [ ] **TRAN-05**: ANALYST/ADMIN can update a transaction
- [ ] **TRAN-06**: ADMIN can delete a transaction (soft delete)
- [ ] **TRAN-07**: Transaction listing supports filters (type, category, date range, pagination, sorting)

### Dashboard (DASH)

- [x] **DASH-01**: User can view summary (total income, expenses, net balance)
- [x] **DASH-02**: User can view totals grouped by category
- [x] **DASH-03**: User can view monthly income/expense trends
- [x] **DASH-04**: User can view recent transactions

### Access Control (RBAC)

- [ ] **RBAC-01**: VIEWER can view own transactions
- [ ] **RBAC-02**: VIEWER can view dashboard summary
- [ ] **RBAC-03**: ANALYST can view all transactions
- [ ] **RBAC-04**: ANALYST can create transactions
- [ ] **RBAC-05**: ANALYST can update transactions
- [ ] **RBAC-06**: ADMIN can delete transactions
- [ ] **RBAC-07**: ADMIN can view all users
- [ ] **RBAC-08**: ADMIN can create/update users
- [ ] **RBAC-09**: ADMIN can deactivate users
- [ ] **RBAC-10**: ADMIN can assign roles

## v2 Requirements

### Notifications

- **NOTF-01**: User receives in-app notifications for large transactions
- **NOTF-02**: Admin receives notifications for user creation

### Export

- **EXPT-01**: User can export transactions to CSV
- **EXPT-02**: User can export dashboard summary to PDF

### Advanced Security

- **SEC-01**: Refresh token rotation with Redis blacklist
- **SEC-02**: Two-factor authentication support
- **SEC-03**: OAuth login (Google, GitHub)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time chat | High complexity, not core to finance dashboard value |
| Multi-tenancy | Requires architectural changes, single-org for v1 |
| Video/image attachments | Not required for financial transaction data |
| Budget tracking | Advanced feature, defer to v2 |
| Recurring transactions | Defer to v2 |
| Webhook notifications | Requires external service integration, defer to v2 |
| Audit logging for all writes | Compliance feature, defer to v2 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 2 | Pending |
| AUTH-02 | Phase 2 | Pending |
| AUTH-03 | Phase 2 | Pending |
| AUTH-04 | Phase 2 | Pending |
| USR-01 | Phase 3 | Pending |
| USR-02 | Phase 3 | Pending |
| USR-03 | Phase 3 | Pending |
| USR-04 | Phase 3 | Pending |
| TRAN-01 | Phase 3 | Pending |
| TRAN-02 | Phase 3 | Pending |
| TRAN-03 | Phase 3 | Pending |
| TRAN-04 | Phase 3 | Pending |
| TRAN-05 | Phase 3 | Pending |
| TRAN-06 | Phase 3 | Pending |
| TRAN-07 | Phase 3 | Pending |
| DASH-01 | Phase 4 | Complete |
| DASH-02 | Phase 4 | Complete |
| DASH-03 | Phase 4 | Complete |
| DASH-04 | Phase 4 | Complete |
| RBAC-01 | Phase 2 | Pending |
| RBAC-02 | Phase 2 | Pending |
| RBAC-03 | Phase 3 | Pending |
| RBAC-04 | Phase 3 | Pending |
| RBAC-05 | Phase 3 | Pending |
| RBAC-06 | Phase 3 | Pending |
| RBAC-07 | Phase 3 | Pending |
| RBAC-08 | Phase 3 | Pending |
| RBAC-09 | Phase 3 | Pending |
| RBAC-10 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 29 total
- Mapped to phases: 29
- Unmapped: 0 ✓

---

*Requirements defined: 2025-04-01*
*Last updated: 2025-04-01 after roadmap creation*