from fastapi import FastAPI

from services.crypto_assets.api.comment_export_routes import router as comment_export_router
from services.crypto_assets.api.routes import router as crypto_router
from services.crypto_assets.api.counterparty_routes import router as counterparty_router

app = FastAPI(title="Crypto Ops Monitor", version="0.1.0")

app.include_router(comment_export_router)
app.include_router(crypto_router)
app.include_router(counterparty_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "crypto-ops-monitor"}
