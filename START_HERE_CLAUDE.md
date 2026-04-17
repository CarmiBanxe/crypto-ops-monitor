Project: crypto-ops-monitor
Goal: довести новый проект Crypto Assets Monitoring Foundation до production-grade foundation этапа 1.

Работаем ТОЛЬКО в этом новом проекте. Не использовать braslina.

Сначала:
1. Изучи структуру текущего проекта.
2. Предложи краткий execution plan.
3. Подготовь foundation architecture в коде.
4. Реализуй Sprint 25 foundation полностью в рамках scope.
5. После каждого крупного блока запускай релевантные тесты.
6. В конце покажи итог по файлам, тестам, рискам и следующему спринту.

Sprint 25 — Crypto Assets Monitoring Foundation + Ailink Wallet Sync (2026-04-17)

Тикет: IL-CAM-01 + IL-AWS-01
Приоритет: P1
Репо: crypto-ops-monitor
Ветка: main

Scope:
- services/crypto_assets/
- append-only ingestion registry
- wallet registry API
- Ailink wallet sync skeleton
- canonical transaction skeleton
- basic transaction read API
- minimum RBAC + audit integration
- ROADMAP.md update

Core entities:
- Network
- Wallet
- Counterparty
- CounterpartyWalletLink
- SourceAccount
- IngestionRun
- RawTransactionEvent
- CanonicalTransaction
- WalletBalanceSnapshot

API:
- GET /crypto/wallets
- POST /crypto/wallets
- GET /crypto/wallets/{wallet_id}
- PATCH /crypto/wallets/{wallet_id}
- POST /crypto/ingestion/ailink-sync
- GET /crypto/ingestion/runs
- GET /crypto/ingestion/runs/{run_id}
- GET /crypto/transactions
- GET /crypto/transactions/{transaction_id}

Rules:
- append-only for raw ingestion data
- no float for money/balances
- Decimal strings in API
- auth required for /crypto/*
- baseline roles: FINANCE_DIRECTOR, HEAD_OF_PAYMENTS, OPERATIONS
- audit logging for wallet create/update and manual sync trigger

Not in scope:
- real blockchain parsers
- exchange/staking adapters
- CSV upload pipeline
- full counterparty UI
- export
- dual control workflow
- fiat conversion
- Xero/accounting

Acceptance:
- DB models + tests exist
- repeated mock Ailink sync creates no duplicates
- missing wallet from next sync is not auto-deleted
- /crypto/wallets and /crypto/transactions basic filters work
- /crypto/* protected by auth
- audit records created
- all tests green

Сейчас начни с:
- предложи plan
- затем создай минимальный skeleton файлов
- затем реализуй foundation block by block
