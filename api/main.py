from fastapi import FastAPI
from services.crypto_assets.api.routes import router as crypto_router

app = FastAPI(title="Crypto Ops Monitor", version="0.1.0")
app.include_router(crypto_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "crypto-ops-monitor"}
