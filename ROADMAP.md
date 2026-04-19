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

## Sprint 34 — Live RPC Connectors (IN PROGRESS)

**Goal**: replace stub `RealEthereumRPCConnector` / `RealBitcoinRPCConnector`
with production HTTP clients, behind `LIVE_MODE` env flag.

### Scope

| # | Block | Description |
|---|-------|-------------|
| B1 | Fix typo | `blockchain_base.py:13` — `deffetch_transactions` → `def fetch_transactions` |
| B2 | Config skeleton | `pydantic-settings`: `ETH_RPC_URL`, `ETH_RPC_API_KEY`, `BTC_RPC_URL`, `BTC_RPC_API_KEY`, `RPC_TIMEOUT_SEC`, `RPC_MAX_RETRIES`, `LIVE_MODE` (default `false`) |
| B3 | Real Ethereum RPC | `httpx` JSON-RPC: `eth_getBalance` for ETH, `eth_call`/`balanceOf` for ERC-20 tokens |
| B4 | Real Bitcoin RPC | `httpx` call to mempool.space or Bitcoin Core JSON-RPC |
| B5 | Retry + circuit breaker | `tenacity`: exponential backoff, 3 retries, open circuit after 5 consecutive failures |
| B6 | Rate limiting | In-memory token bucket per connector, configurable via env |
| B7 | LIVE_MODE switching | `SourceRegistry` returns `Real*` if `LIVE_MODE=true`, else `Mock*` (fallback) |
| B8 | Tests | `respx` HTTP mocking + VCR cassettes: happy path, RPC error, timeout, rate limit, circuit open |
| B9 | Refresh orchestrator integration | `refresh_orchestrator.py` aware of `LIVE_MODE`, graceful fallback on connector errors |
| B10 | Docs | `README.md` section "Live RPC", `.env.example`, `ROADMAP.md` marks DONE |

### Dependencies to add

- `httpx` (already present via FastAPI)
- `tenacity >= 8.0`
- `pydantic-settings >= 2.0`
- `respx >= 0.20` (dev)

### Acceptance

- `LIVE_MODE=false pytest -q` — all tests green (new + existing)
- `LIVE_MODE=true ETH_RPC_URL=... pytest -q` — RPC calls mocked via `respx` cassettes, green
- Without `ETH_RPC_URL` or `BTC_RPC_URL` set, LIVE connectors fall back to mocks, no crash
- `gitleaks` — clean (no leaked keys in commits)
- `ruff check .`, `mypy .` — zero errors
- Coverage not below current baseline

### Not in scope

- Live Kraken / Binance SDK (Sprint 35 — exchange adapters)
- Postgres migration (Sprint 36 — persistence hardening)
- WebSocket subscriptions for live events
- Historical backfill pagination for large date ranges

### Blockers / open questions

- **API keys**: none provisioned yet — initial work uses public endpoints (publicnode.com for ETH, mempool.space for BTC), optional key support via env
- **Rate limits**: public endpoints ~10 req/sec — token bucket must respect

