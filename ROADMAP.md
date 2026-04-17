# Crypto Ops Monitor — ROADMAP

## Sprint 25 — Crypto Assets Monitoring Foundation (2026-04-17)

### Status: COMPLETE

### Scope delivered
- Domain models: Network, Wallet, Counterparty, CounterpartyWalletLink, SourceAccount, IngestionRun, RawTransactionEvent, CanonicalTransaction, WalletBalanceSnapshot
- Append-only ingestion registry
- Ailink wallet sync skeleton (mock adapter, idempotent upsert)
- Wallet registry API: GET/POST/GET-by-id/PATCH /crypto/wallets
- Ingestion API: POST /crypto/ingestion/ailink-sync, GET /crypto/ingestion/runs, GET /crypto/ingestion/runs/{id}
- Transaction read API: GET /crypto/transactions, GET /crypto/transactions/{id}
- Auth baseline: Bearer token stub, roles FINANCE_DIRECTOR / HEAD_OF_PAYMENTS / OPERATIONS
- Audit logging: wallet create/update, manual sync trigger
- Test isolation: in-memory SQLite with StaticPool + dependency_overrides

### Not in scope (future sprints)
- Real blockchain parsers (11+ networks)
- Exchange/staking API adapters (Kraken, Binance, Stillman, Overstake)
- CSV ingestion templates
- Counterparty full CRUD UI
- Folder tree / shared tagging UX
- Transaction comments/tags
- Export CSV/TSV
- Balance reconciliation engine
- Dual control approvals flow
- Fiat conversion, Xero, accounting postings

### Metrics
- Tests: 9
- API endpoints: 9 (/health + 8 /crypto/*)
- Modules: services/crypto_assets/{models,repositories,schemas,service,api,tests}

## Sprint 26 — Planned
- Counterparty CRUD + wallet linking
- Transaction comments/tags
- Filtered export CSV/TSV
- RBAC role enforcement (OPERATIONS read-only restrictions)
- Dual control for critical reference data changes
