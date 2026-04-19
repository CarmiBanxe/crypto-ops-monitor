# Crypto Ops Monitor — ROADMAP

## FULLY DELIVERED — 100%

## Sprint History

| Sprint | Scope | Status |
|--------|-------|--------|
| 25 | Foundation: domain models, wallet registry, Ailink sync, auth/audit | DONE |
| 26 | Counterparty CRUD + linking, transaction comments/tags, CSV/TSV export | DONE |
| 27 | Wallet folders/tags, RBAC enforcement, extended filters | DONE |
| 28 | Folders/tags/approvals API, dual control workflow | DONE |
| 29 | Balance snapshots, blockchain connector skeleton, balance API | DONE |
| 30 | BTC/ETH/Polygon/BSC connectors, Kraken/Binance/Overstake adapters, CSV import, source registry | DONE |
| 31 | Refresh-All orchestrator, reconciliation, operational API | DONE |
| 32 | Fiat valuation, Xero integration, classification rules, frozen reports, travel rule, real RPC scaffold | DONE |
| 33 | CSV import, security fixes, refresh orchestration hardening, quality cleanup | DONE |

## Post-v1.0.0 Hardening

| PR | Scope | Commit | Status |
|----|-------|--------|--------|
| #1 | Stabilize sprint31 operational API tests (late-bound `SessionLocal`) | `000d5c7` | MERGED |
| #2 | CI baseline: ruff + mypy + pytest + gitleaks, `[dev]` extras, StrEnum migration, 68 lint fixes | `f59330a` | MERGED |
| — | Branch protection on `main` with required status checks + linear history | — | ACTIVE |

## Final Coverage

- 18+ core entities
- 40+ API endpoints
- 4 blockchain + 2 exchange + 1 staking connectors
- Fiat conversion, Xero postings, classification rules
- Frozen reports, travel rule records
- Full audit, RBAC, dual control, append-only
- Real RPC connector scaffolds ready for production wiring

## Quality Gate

- `ruff check .` — 0 errors (select E, F, W, I, UP, B, SIM, RUF)
- `mypy services api banxe_mcp --ignore-missing-imports` — 0 errors
- `pytest -q` — 100 passed
- `gitleaks` — clean
- CI on every PR via `.github/workflows/ci.yml`
- `main` protected with required checks + linear history + no force push
