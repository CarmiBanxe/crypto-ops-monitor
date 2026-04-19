# Crypto Ops Monitor

BANXE Crypto Assets Monitoring Foundation — production-grade backend for tracking
custodial (Ailink) and non-custodial crypto wallets, exchange accounts, and
staking positions with append-only ledger, RBAC, dual-control, Xero integration,
and travel-rule records.

## Status

**v1.0.0** released. All 9 sprints (25–33) delivered. Post-v1.0.0 hardening
completed: CI baseline, type-checking, branch protection.

## Quick Start

```bash
git clone git@github.com:CarmiBanxe/crypto-ops-monitor.git
cd crypto-ops-monitor
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest -q

# Run API
uvicorn api.main:app --reload
```

## Architecture

- **Layer**: FastAPI + SQLAlchemy 2.0 + Pydantic v2
- **Data model**: 18+ entities across wallets, counterparties, ingestion runs,
  canonical transactions, balance snapshots, folders, tags, approvals, fiat
  rates, Xero postings, classification rules, frozen reports, travel-rule records
- **Connectors**: Bitcoin, Ethereum, Polygon, BSC (RPC scaffold), Kraken,
  Binance, Overstake (mock adapters ready for live credentials)
- **Ports**: 40+ REST endpoints under `/crypto/*` — wallets, counterparties,
  balances, transactions, ingestion, operational, comments, export

## Quality Gates

All PRs run the following on GitHub Actions before merge:

- `ruff check .` — lint (E, F, W, I, UP, B, SIM, RUF)
- `mypy services api banxe_mcp --ignore-missing-imports` — type-checking
- `pytest -q` — 100 tests
- `gitleaks` — secret scanning

`main` branch is protected with required status checks, linear history, and no
force pushes.

## Development

See `START_HERE_CLAUDE.md` for project conventions (append-only ingestion,
Decimal-only money, canonical transactions, RBAC roles).

See `ROADMAP.md` for sprint history and final coverage.

## License

MIT — see `LICENSE`.
