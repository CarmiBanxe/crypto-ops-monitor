# Crypto Ops Monitor — ROADMAP

## Stage 1 — COMPLETE (100%)

Internal crypto monitoring platform: collecting, aggregating, storing and displaying crypto wallet/exchange/staking transactions and balances. Read-only monitoring, no transaction execution, no fiat conversion.

## Progress Tracker

| Sprint | Scope | Status |
|--------|-------|--------|
| 25 | Foundation: domain models, wallet registry API, Ailink sync skeleton, auth/audit baseline | DONE |
| 26 | Counterparty CRUD + linking, transaction comments/tags, CSV/TSV export | DONE |
| 27 | Wallet folders/tags, RBAC enforcement, extended filters, counterparty routing | DONE |
| 28 | Folders/tags/approvals API, dual control workflow | DONE |
| 29 | Balance snapshots, blockchain connector skeleton, balance API | DONE |
| 30 | Blockchain connectors (BTC, ETH, Polygon, BSC), exchange adapters (Kraken, Binance), staking (Overstake), CSV import, source registry | DONE |
| 31 | Refresh-All orchestrator, reconciliation service, operational API, production hardening | DONE |

## Final Metrics
- Tests: 48 green
- API endpoints: 35+
- Models: 13 core entities
- Connectors: 4 blockchain + 2 exchange + 1 staking
- Source registry with adapter injection
- CSV import pipeline with fingerprint dedup
- RBAC enforcement on all write endpoints
- Dual control approval workflow
- Append-only raw ingestion + canonical transactions
- Balance snapshots + reconciliation
- Full audit trail
- Version 1.0.0

## Stage 2 (Future)
- Real blockchain RPC integrations (replace mocks)
- Production credentials management
- Fiat conversion (PLN, EUR)
- Xero accounting integration
- Transaction classification rules
- Saved reports (frozen snapshots)
- Advanced counterparty analytics (travel rule)
