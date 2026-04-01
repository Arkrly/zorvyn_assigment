# Domain Pitfalls

**Project:** FinanceBoard - Finance Dashboard Backend  
**Domain:** Financial Data Processing & Access Control System  
**Researched:** 2026-04-01  
**Confidence:** HIGH

This document catalogs critical, moderate, and minor pitfalls specific to finance dashboard backend development. Each pitfall includes warning signs, prevention strategies, and phase mapping recommendations.

---

## Critical Pitfalls

### 1. Access Control Bypass in Transaction Endpoints

**What Goes Wrong:** Users can access, modify, or delete transactions they should not have permission to view or edit. VIEWER role should only see their own transactions, but implementation bugs may allow them to see all transactions or access other users' data.

**Why It Happens:** 
- Incomplete role checks in endpoint handlers
- Missing ownership validation for resource-level permissions
- Relying solely on route-level dependencies without object-level checks
- The PS.md specifies VIEWER can only "View own transactions" but ANALYST can "View all transactions" - this distinction is often missed in implementation

**Consequences:**
- Data privacy violations (users seeing other users' financial data)
- Compliance violations (GDPR, financial regulations)
- Loss of user trust in the platform

**Prevention:**
- Implement ownership verification in service layer for every sensitive operation
- Add explicit user_id or ownership checks in transaction queries
- Create reusable authorization helpers that check both role AND ownership
- Add integration tests that verify each role can only access permitted resources

**Warning Signs:**
- API returns transactions for user IDs other than the authenticated user's ID
- VIEWER role can access /transactions endpoint with filters for other users
- No 403 responses when accessing unauthorized resources

**Phase Mapping:** This must be addressed in Phase 2 (Authentication & Authorization) - critical path item before any data access

---

### 2. Using Float/Double Instead of Decimal for Financial Amounts

**What Goes Wrong:** Financial calculations produce rounding errors that compound over time. A transaction of $10.25 stored as float may become $10.249999999999998, and after multiple operations, cents disappear or appear incorrectly.

**Why It Happens:**
- Defaulting to Python float type instead of Decimal
- PostgreSQL numeric/decimal types not configured properly
- ORM mapping that converts Decimal to float automatically
- Calculations in Python that mix Decimal and float

**Consequences:**
- Account balances that don't add up correctly
- Rounding discrepancies in financial reports
- Audit failures when penny-perfect accuracy is required
- Potential financial loss from rounding exploitation

**Prevention:**
- PS.md already uses `Decimal(12, 2)` in the model - this is correct
- Ensure SQLAlchemy mapping uses `Numeric` or `DECIMAL` PostgreSQL type
- Never perform arithmetic between Decimal and float values
- Use `decimal.Decimal` for all Python-side calculations
- Configure Pydantic schemas to validate and serialize as Decimal

**Warning Signs:**
- Tests show results like 0.6099999999999999 instead of 0.61
- Dashboard totals don't match manual calculation
- Floating point operations in transaction service code

**Phase Mapping:** Already addressed in PS.md design (Decimal type). Verify implementation in Phase 1 (Data Models & Migrations).

---

### 3. Missing or Incomplete Audit Trail

**What Goes Wrong:** Financial systems require complete audit trails showing who did what and when. Without proper logging, there's no way to verify compliance, investigate fraud, or reconstruct events.

**Why It Happens:**
- No audit log table or logging mechanism
- Only storing final state without change history
- Missing "created_by" and "updated_by" fields on transactions
- No logging of DELETE operations (even soft deletes need audit)

**Consequences:**
- Inability to comply with financial regulations (SOX, PCI-DSS)
- No recourse for fraud investigation
- Cannot reconcile discrepancies
- Failed compliance audits

**Prevention:**
- Add created_by and updated_by UUID fields to Transaction model
- Create audit_log table for tracking all write operations
- Log who created/modified/deleted each transaction with timestamps
- Consider adding a "change_reason" field for soft deletes
- Use SQLAlchemy events to auto-populate audit fields

**Warning Signs:**
- No way to determine who created a transaction
- Transaction history shows no modification trail
- Soft delete doesn't record who deleted or when

**Phase Mapping:** Address in Phase 3 (Core Features - Transactions). Add audit fields to migration and update service layer to populate them.

---

### 4. JWT Token Security Vulnerabilities

**What Goes Wrong:** JWT tokens are improperly validated or generated, allowing attackers to forge tokens, perform timing attacks, or hijack sessions.

**Why It Happens:**
- Using weak SECRET_KEY or hardcoded values
- Not validating token signature properly
- Accepting tokens with "none" algorithm
- Missing expiration validation
- Timing-attack-vulnerable comparisons
- Not storing token version/handle for revocation

**Consequences:**
- Account takeover via forged tokens
- Privilege escalation (attacker creates ADMIN tokens)
- Stolen tokens remain valid indefinitely
- Unable to revoke compromised tokens

**Prevention:**
- Use strong SECRET_KEY from environment variables (PS.md uses this pattern)
- Explicitly specify and validate algorithm (HS256)
- Set reasonable ACCESS_TOKEN_EXPIRE_MINUTES (PS.md uses 30 - good)
- Use constant-time comparison for token validation
- Implement refresh token rotation with blacklist (mentioned in future improvements)
- Validate all claims: exp, iat, issuer if applicable

**Warning Signs:**
- Token validation accepts "alg: none"
- No expiration error when token is expired
- Identical response times for valid/invalid tokens (timing attack)

**Phase Mapping:** Address in Phase 2 (Authentication & Authorization). Security review before deployment.

---

## Moderate Pitfalls

### 5. Soft Delete Not Applied Consistently

**What Goes Wrong:** Transactions marked as deleted (is_deleted=True) are still returned in queries, or worse, hard deletes occur accidentally, permanently losing financial data.

**Why It Happens:**
- Missing global query filter for is_deleted
- Some queries explicitly query is_deleted=False while others don't
- ORM queries that bypass the default filter
- No database constraint preventing hard deletes

**Consequences:**
- Deleted transactions appear in dashboards
- Data inconsistency between reports
- Legal/compliance issues if "deleted" data is referenced
- Financial records cannot be fully reconstructed

**Prevention:**
- Use SQLAlchemy where clause or custom base query class to filter is_deleted by default
- Add database unique constraint or trigger to prevent hard deletes
- Make DELETE operation explicitly update is_deleted instead
- Add integration tests that verify deleted transactions don't appear in any endpoint

**Warning Signs:**
- Deleted transactions visible in GET /transactions
- No is_deleted filter in dashboard aggregation queries
- Hard DELETE SQL queries in code

**Phase Mapping:** Verify in Phase 1 (Data Models). Ensure all queries filter by is_deleted=False.

---

### 6. Input Validation Gaps for Financial Data

**What Goes Wrong:** Invalid amounts, dates, or categories are accepted, causing data integrity issues or security vulnerabilities.

**Why It Happens:**
- Missing Pydantic validation on amount (negative values, zero, overflow)
- No bounds checking on date ranges (future dates, extreme past dates)
- Category field accepts arbitrary strings without allowlist
- Missing sanitization of notes field (XSS, injection)

**Consequences:**
- Negative income or positive expenses (invalid accounting)
- Corrupted dashboard analytics
- Potential injection attacks via notes field
- Invalid data that breaks reports

**Prevention:**
- Add Pydantic constraints: ge=0 for amount, max digits for precision
- Validate date ranges: not in far future for transactions
- Use Enum for transaction type (INCOME/EXPENSE)
- Consider allowlist for common categories or validate format
- Sanitize notes field with length limits and content validation

**Warning Signs:**
- POST /transactions accepts negative amount for income
- Transaction date in year 3025 accepted
- Arbitrary category strings stored without validation

**Phase Mapping:** Address in Phase 1 (Data Models) and Phase 3 (Core Features - Transactions).

---

### 7. Race Conditions in Concurrent Financial Operations

**What Goes Wrong:** Multiple concurrent operations on the same account or transaction cause lost updates, incorrect balances, or over/under allocation of funds.

**Why It Happens:**
- No optimistic locking on transaction updates
- Read-modify-write patterns without proper isolation
- Multiple dashboard calculations running simultaneously
- Missing database transactions for multi-step operations

**Consequences:**
- Two simultaneous transactions result in only one being recorded
- Dashboard totals don't match actual transactions
- Lost money or incorrect account balances
- Difficult-to-reproduce bugs that appear intermittently

**Prevention:**
- Use database-level locking (SELECT FOR UPDATE) for balance modifications
- Implement optimistic locking with version fields on transactions
- Ensure dashboard aggregations use consistent read isolation
- Wrap multi-step operations in proper database transactions

**Warning Signs:**
- Concurrent transaction creation results in duplicate or missing entries
- Dashboard totals vary on successive calls with same parameters
- No transaction management in service layer

**Phase Mapping:** Address in Phase 3 (Core Features) and Phase 4 (Dashboard APIs).

---

### 8. Performance Issues with Large Datasets

**What Goes Wrong:** Dashboard endpoints timeout or run slowly as transaction volume grows, blocking users and causing timeouts.

**Why It Happens:**
- No pagination on list endpoints (PS.md has pagination - good)
- Missing database indexes on date, user_id, category
- Full table scans for dashboard aggregations
- N+1 query problems in ORM
- No query result caching

**Consequences:**
- API timeouts under load
- Poor user experience
- Dashboard unusable for users with many transactions
- Potential database overload

**Prevention:**
- Add indexes: (user_id, date), (user_id, type), (category)
- Implement query result caching for dashboard summaries
- Use database-level aggregation (SUM, COUNT) instead of Python
- Implement cursor-based pagination for large result sets
- Add connection pooling configuration for PostgreSQL
- Consider materialized views for frequent aggregations

**Warning Signs:**
- GET /transactions slow with >1000 records
- Dashboard summary takes >5 seconds with 10K transactions
- Missing indexes shown in EXPLAIN ANALYZE

**Phase Mapping:** Address in Phase 1 (Database Setup) with proper indexes, and Phase 4 (Dashboard APIs) with caching.

---

## Minor Pitfalls

### 9. Error Messages Leaking Sensitive Information

**What Goes Wrong:** API error responses expose internal details like database schemas, file paths, environment variables, or user IDs that shouldn't be visible to clients.

**Why It Happens:**
- Using default exception handlers without custom error responses
- Propagating internal exceptions to API responses
- Verbose logging in production
- Including stack traces in error responses

**Consequences:**
- Information disclosure to attackers
- Security vulnerabilities revealed
- User IDs exposed in error messages
- Internal architecture exposed

**Prevention:**
- Create custom exception handlers that return sanitized errors
- Log full details server-side but return generic messages to clients
- Use error codes instead of messages for client handling
- Mask or omit user IDs in error responses
- Configure production error handlers to hide stack traces

**Warning Signs:**
- 500 errors show Python tracebacks
- Database connection errors reveal database hostnames
- Validation errors show internal field names

**Phase Mapping:** Address in Phase 2 (Error Handling) or throughout implementation.

---

### 10. Missing Rate Limiting

**What Goes Wrong:** API endpoints can be hammered by malicious actors or runaway clients, causing service degradation or enabling enumeration attacks.

**Why It Happens:**
- No rate limiting middleware configured
- Not tracking request rates per user/IP
- Public endpoints without protection
- Missing limits on write operations

**Consequences:**
- API service degradation or outage
- Brute force attacks on authentication
- Resource exhaustion
- Ability to enumerate valid user emails via /auth/register

**Prevention:**
- Implement rate limiting middleware (e.g., slowapi for FastAPI)
- Configure different limits for authenticated vs public endpoints
- Add rate limits: auth endpoints (5/min), write operations (60/min), reads (120/min)
- Return 429 Too Many Requests with proper headers
- Log rate limit exceeded events for monitoring

**Warning Signs:**
- No rate limiting in middleware
- Auth endpoints don't have brute-force protection
- No 429 responses observed under load

**Phase Mapping:** Address in Phase 2 (Security Hardening) or production deployment phase.

---

### 11. Inconsistent Date/Time Handling

**What Goes Wrong:** Dates are stored, queried, and returned in inconsistent formats or time zones, causing analytics errors and user confusion.

**Why It Happens:**
- Storing naive datetimes without timezone info
- Mixing UTC and local time in queries
- Date filters not accounting for user timezone
- Different date formats in different endpoints

**Consequences:**
- Transactions appearing on wrong dates in dashboards
- Month-end reports incorrect by one day
- User sees transactions with dates that don't match their intent
- Analytics aggregations off by timezone offset

**Prevention:**
- Use timezone-aware datetimes (UTC storage recommended)
- Store all timestamps in UTC, convert to user timezone in responses
- Use ISO 8601 format consistently in APIs
- Accept timezone in date filter parameters
- Document timezone behavior in API specification

**Warning Signs:**
- Transaction dates shift when viewed in different contexts
- Dashboard totals change based on time of day queried
- No timezone information in datetime fields

**Phase Mapping:** Address in Phase 1 (Data Models) - ensure proper datetime types and timezone handling.

---

### 12. Insufficient Test Coverage for Financial Logic

**What Goes Wrong:** Critical financial calculations and authorization rules lack test coverage, allowing bugs to reach production.

**Why It Happens:**
- Only testing happy path
- No tests for edge cases (zero amounts, boundary dates)
- Missing authorization tests for each role
- No integration tests across multiple components
- Dashboard logic not tested separately from API

**Consequences:**
- Bugs in production that affect financial accuracy
- Authorization bypasses undetected
- Dashboard calculations wrong under certain conditions
- Regressions go unnoticed

**Prevention:**
- Write comprehensive tests for all calculation logic
- Test each role permission explicitly
- Add integration tests for complete workflows
- Test dashboard calculations with various date ranges and data volumes
- Include negative tests (invalid inputs, unauthorized access)
- Use property-based testing for calculations

**Warning Signs:**
- Test coverage below 80% for financial modules
- No tests for authorization layers
- Dashboard tests only check response format, not values

**Phase Mapping:** Address throughout implementation - each phase should include tests.

---

## Phase-Specific Warnings

| Phase | Topic | Likely Pitfall | Mitigation |
|-------|-------|----------------|------------|
| Phase 1 | Data Models | Using wrong types for financial data | Verify Decimal for amounts, UUID for IDs |
| Phase 2 | Auth | JWT security vulnerabilities | Use strong secrets, validate all claims, constant-time comparison |
| Phase 3 | Transactions | Missing soft delete filtering | Add global query filter for is_deleted=False |
| Phase 3 | Transactions | Missing audit trail | Add created_by, updated_by fields and audit logging |
| Phase 4 | Dashboard | Performance at scale | Add indexes, implement caching, optimize queries |
| Phase 4 | Dashboard | Calculation accuracy | Test with large datasets, verify against known results |

---

## Summary: Critical Path Items

1. **Access Control** - Verify every endpoint checks role AND ownership
2. **Decimal Type** - Confirm implementation uses Decimal, not float
3. **Audit Trail** - Add audit fields and logging before data access
4. **JWT Security** - Hardening token handling before production
5. **Soft Delete** - Global filter to exclude deleted records

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Access Control Pitfalls | HIGH | Well-documented RBAC vulnerability patterns |
| Decimal vs Float | HIGH | Stack Overflow consensus is definitive |
| Audit Trail Gaps | HIGH | Financial compliance requirement |
| JWT Security | HIGH | OWASP guidelines provide clear direction |
| Soft Delete Consistency | MEDIUM | Common in practice but implementation-specific |
| Performance | MEDIUM | Depends on scale expectations |

---

## Sources

- Stack Overflow: "Why not use Double or Float to represent currency?" - floating point precision issues
- FastAPI Security Documentation - JWT implementation patterns
- OWASP API Security Top 10 - authorization and rate limiting
- SQLAlchemy 2.0 Documentation - async session management
- PostgreSQL Documentation - decimal type and indexing