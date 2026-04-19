from fastapi.testclient import TestClient

from api.main import app
from services.crypto_assets.models import Network, Wallet, WalletSourceType, WalletType

client = TestClient(app)


def auth_headers(token: str = "finance-director-token") -> dict:
    return {"Authorization": f"Bearer {token}"}


def seed_wallet_via_db(db, address: str = "0xop001"):
    network = db.query(Network).filter_by(identifier="ethereum").first()
    if not network:
        network = Network(name="Ethereum", identifier="ethereum")
        db.add(network)
        db.commit()
        db.refresh(network)

    wallet = db.query(Wallet).filter_by(network_id=network.id, address=address).first()
    if not wallet:
        wallet = Wallet(
            address=address,
            display_name="Op Wallet",
            network_id=network.id,
            source_type=WalletSourceType.MANUAL,
            wallet_type=WalletType.NON_CUSTODY,
        )
        db.add(wallet)
        db.commit()
        db.refresh(wallet)

    return wallet.id


def test_refresh_all_requires_auth():
    response = client.post("/crypto/ingestion/refresh-all")
    assert response.status_code == 401


def test_refresh_all_ops_blocked():
    response = client.post(
        "/crypto/ingestion/refresh-all",
        headers={"Authorization": "Bearer operations-token"},
    )
    assert response.status_code == 403


def test_refresh_all_finance_director_works(test_db):
    db = app.dependency_overrides[next(iter(app.dependency_overrides))]()
    db = next(db)
    try:
        seed_wallet_via_db(db, "0xop-refresh")
    finally:
        db.close()

    response = client.post(
        "/crypto/ingestion/refresh-all?token_symbol=USDC",
        headers=auth_headers(),
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "run_id" in data
    assert "status" in data
    assert "stats" in data


def test_reconciliation_coverage(test_db):
    db_gen = app.dependency_overrides[next(iter(app.dependency_overrides))]()
    db = next(db_gen)
    try:
        seed_wallet_via_db(db, "0xop-recon")
    finally:
        db.close()

    response = client.get(
        "/crypto/reconciliation/coverage?token_symbol=USDC",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_wallets" in data
    assert "coverage_pct" in data


def test_reconcile_wallet_endpoint(test_db):
    db_gen = app.dependency_overrides[next(iter(app.dependency_overrides))]()
    db = next(db_gen)
    try:
        wallet_id = seed_wallet_via_db(db, "0xop-reconcile-one")
    finally:
        db.close()

    response = client.get(
        f"/crypto/reconciliation/wallet/{wallet_id}?token_symbol=USDC&expected=100.00&tolerance=0.01",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_id"] == wallet_id
    assert data["status"] in ("OK", "MISMATCH", "NO_DATA")


def test_health_reports_stage_1():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["stage"] == "1"
    assert data["version"] == "1.0.0"
