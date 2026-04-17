# Crypto Ops Monitor — ROADMAP

## Stage 1 Overview
Internal platform for collecting, aggregating, storing and displaying crypto wallet/exchange/staking transactions and balances. Read-only monitoring, no transaction execution, no fiat conversion. Covers ~30% of Breezing functionality.

**Priority:** MAXIMUM — annual reporting deadline in ~2 months.

## Progress Tracker

| Sprint | Scope | Status |
|--------|-------|--------|
| 25 | Foundation: domain models, wallet registry API, Ailink sync skeleton, auth/audit baseline | DONE |
| 26 | Counterparty CRUD + linking, transaction comments/tags, CSV/TSV export | DONE |
| 27 | Wallet folders/tags, RBAC enforcement, extended filters, counterparty routing | DONE |
| 28 | Folders/tags/approvals API, dual control workflow | DONE |
| 29 | Balance snapshots, blockchain connector skeleton, balance API | DONE |
| 30 | Additional blockchain networks, exchange/staking adapters, CSV upload | NEXT |
| 31 | "Get Latest Transactions All", balance reconciliation, production hardening | PLANNED |

## Current Metrics
- Tests: 28 green
- API endpoints: 30+
- Models: 13 core entities
- Branches merged: sprint-25 through sprint-29

## Stage 1 Completion Estimate
~75% of Stage 1 delivered. Remaining: real blockchain connectors (11+ networks), exchange/staking API adapters, CSV upload pipeline, reconciliation engine.

## Out of Stage 1
- Fiat conversion (PLN, EUR)
- Xero integration
- Transaction classification rules
- Reconciliation with WonderWaffle/Ailink
- Extended counterparty analytics
- Saved reports (frozen snapshots)
