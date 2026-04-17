# Crypto Ops Monitor — ROADMAP

## Stage 1 Overview
Internal platform for collecting, aggregating, storing and displaying crypto wallet/exchange/staking transactions and balances. Read-only monitoring, no transaction execution, no fiat conversion. Covers ~30% of Breezing functionality.

**Priority:** MAXIMUM — annual reporting deadline in ~2 months.

## Progress Tracker

| Sprint | Scope | Status |
|--------|-------|--------|
| 25 | Foundation: domain models, wallet registry API, Ailink sync skeleton, auth/audit baseline | DONE |
| 26 | Counterparty CRUD + linking, transaction comments/tags, export CSV/TSV | NEXT |
| 27 | Wallet folders/tags, extended filters/search, RBAC enforcement, dual control | PLANNED |
| 28 | Blockchain connectors (first 3-4 networks), balance snapshots + visibility | PLANNED |
| 29 | Remaining blockchain networks, exchange APIs, staking APIs, CSV upload pipeline | PLANNED |
| 30 | "Get Latest Transactions All", balance consistency, reconciliation, hardening | PLANNED |

---

## Sprint 25 — Foundation (2026-04-17) — DONE

### Delivered
- 9 core entities: Network, Wallet, Counterparty, CounterpartyWalletLink, SourceAccount, IngestionRun, RawTransactionEvent, CanonicalTransaction, WalletBalanceSnapshot
- Append-only ingestion registry
- Ailink wallet sync skeleton (mock adapter, idempotent upsert, no auto-delete)
- Wallet registry API: GET/POST/GET-by-id/PATCH /crypto/wallets
- Ingestion API: POST /crypto/ingestion/ailink-sync, GET /crypto/ingestion/runs, GET /crypto/ingestion/runs/{id}
- Transaction read API: GET /crypto/transactions, GET /crypto/transactions/{id}
- Auth baseline: Bearer token stub, roles FINANCE_DIRECTOR / HEAD_OF_PAYMENTS / OPERATIONS
- Audit logging: wallet create/update, manual sync trigger
- Test isolation: in-memory SQLite with StaticPool + dependency_overrides

### Metrics
- Tests: 9 | API endpoints: 9 | Files: 45 | Lines: 1254

---

## Sprint 26 — Counterparty + Comments + Export — NEXT

### Planned scope
- Counterparty CRUD: create, update, delete
- Wallet <-> Counterparty linking (many-to-many, manual)
- Auto-attribution: transactions inherit counterparty from linked wallet
- Transaction comments (author, timestamp)
- Transaction tags (user-defined, filterable)
- Filtered export CSV/TSV (current view with applied filters)
- Audit logging for counterparty and link changes

---

## Sprint 27 — Folders + Filters + RBAC + Dual Control — PLANNED

### Planned scope
- Wallet folders/tags with tree navigation panel
- Extended transaction filters: token, network, direction, period, counterparty, tags, folders
- Flexible date range picker
- RBAC enforcement: OPERATIONS restricted to assigned wallets/folders
- Dual control workflow for critical reference data changes (wallet delete, counterparty edit, link changes)
- Approval requests table with initiator/approver/diff/status

---

## Sprint 28 — Blockchain Connectors + Balances — PLANNED

### Planned scope
- Blockchain transaction ingestion adapters (first 3-4 networks)
- Per-network parser/adapter interface
- Checkpoint state per wallet/network (avoid full rescans)
- Balance snapshots: wallet_id, token, observed_at, amount, source_type
- Current balance projection for dashboard
- Last sync time visibility per wallet
- Anomaly detection flags for balance mismatches

---

## Sprint 29 — Source Expansion — PLANNED

### Planned scope
- Remaining blockchain networks (total 11+)
- Exchange API adapters: Kraken, Binance, Stillman
- Staking API adapters: Overstake and others
- CSV upload pipeline: file upload, provider mapping templates, row fingerprint dedup
- Import error reporting with problem row details
- Source account management UI

---

## Sprint 30 — Operational Readiness — PLANNED

### Planned scope
- "Get Latest Transactions All" button: trigger full refresh across all sources
- Background job orchestration with status visibility
- Balance consistency checks vs blockchain
- Reconciliation reporting
- Operational observability: ingestion errors, parser errors, duplicate collisions
- Production hardening: error handling, retries, rate limiting
- Documentation and runbooks

---

## Out of Stage 1 (Future stages)
- Fiat conversion (PLN, EUR)
- Xero integration: chart of accounts, automatic postings
- Transaction classification rules (wallet + network + token -> account X)
- WonderWaffle / Ailink reconciliation
- Extended counterparty analytics (travel rule)
- Saved reports (frozen data snapshots)
