from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.crypto_assets.api.balance_routes import router as balance_router
from services.crypto_assets.api.comment_export_routes import router as comment_export_router
from services.crypto_assets.api.counterparty_routes import router as counterparty_router
from services.crypto_assets.api.operational_routes import router as operational_router
from services.crypto_assets.api.routes import router as crypto_router
from services.crypto_assets.bootstrap import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Deterministic DB bootstrap: register all models and create tables.
    init_db()
    yield


app = FastAPI(title="Crypto Ops Monitor", version="1.0.0", lifespan=lifespan)
app.include_router(comment_export_router)
app.include_router(balance_router)
app.include_router(crypto_router)
app.include_router(counterparty_router)
app.include_router(operational_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "crypto-ops-monitor", "stage": "1", "version": "1.0.0"}
