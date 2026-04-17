from fastapi.testclient import TestClient

from api.main import app
from services.crypto_assets.audit import AUDIT_LOG

client = TestClient(app)


def auth_headers(token: str = "finance-director-token") -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_crypto_requires_auth():
    response = client.get("/crypto/wallets")
    assert response.status_code == 401


def test_create_and_get_wallet():
    response = client.post(
        "/crypto/wallets",
        headers=auth_headers(),
        json={
            "address": "0x999",
            "display_name": "API Wallet",
            "network_id": 1,
            "source_type": "MANUAL",
            "source_ref": "manual-api",
            "wallet_type": "NON_CUSTODY",
            "status": "ACTIVE",
        },
    )
    assert response.status_code == 200, response.text
    wallet_id = response.json()["id"]

    get_response = client.get(f"/crypto/wallets/{wallet_id}", headers=auth_headers())
    assert get_response.status_code == 200
    assert get_response.json()["address"] == "0x999"


def test_ailink_sync_and_runs():
    response = client.post("/crypto/ingestion/ailink-sync", headers=auth_headers())
    assert response.status_code == 200, response.text
    run_id = response.json()["id"]

    runs = client.get("/crypto/ingestion/runs", headers=auth_headers())
    assert runs.status_code == 200
    assert any(item["id"] == run_id for item in runs.json())


def test_audit_log_records_actions():
    AUDIT_LOG.clear()
    create_response = client.post(
        "/crypto/wallets",
        headers=auth_headers(),
        json={
            "address": "0x777",
            "display_name": "Audit Wallet",
            "network_id": 1,
            "source_type": "MANUAL",
            "source_ref": "manual-audit",
            "wallet_type": "NON_CUSTODY",
            "status": "ACTIVE",
        },
    )
    assert create_response.status_code == 200
    assert any(entry["action"] == "CREATE_WALLET" for entry in AUDIT_LOG)
