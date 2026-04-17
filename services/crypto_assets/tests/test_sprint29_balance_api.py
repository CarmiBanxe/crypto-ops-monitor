from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def auth_headers(token: str = "finance-director-token") -> dict:
    return {"Authorization": f"Bearer {token}"}


def seed_wallet_via_api(address="0xapi-bal"):
    wallets = client.get("/crypto/wallets", headers=auth_headers()).json()
    for wallet in wallets:
        if wallet["address"] == address:
            return wallet["id"]
    response = client.post(
        "/crypto/wallets",
        headers=auth_headers(),
        json={
            "address": address,
            "display_name": "API Balance Wallet",
            "network_id": 1,
            "source_type": "MANUAL",
            "wallet_type": "NON_CUSTODY",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_record_and_list_balance_snapshots():
    wallet_id = seed_wallet_via_api("0xapi-bal-1")
    response = client.post(
        f"/crypto/wallets/{wallet_id}/balances",
        headers=auth_headers(),
        json={
            "wallet_id": wallet_id,
            "token_symbol": "USDC",
            "observed_at": "2026-04-17T20:00:00Z",
            "amount": "2500.00",
            "source_type": "MANUAL",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["token_symbol"] == "USDC"

    list_response = client.get(
        f"/crypto/wallets/{wallet_id}/balances",
        headers=auth_headers(),
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1


def test_operations_cannot_record_balance():
    wallet_id = seed_wallet_via_api("0xapi-bal-ops")
    response = client.post(
        f"/crypto/wallets/{wallet_id}/balances",
        headers={"Authorization": "Bearer operations-token"},
        json={
            "wallet_id": wallet_id,
            "token_symbol": "USDC",
            "observed_at": "2026-04-17T20:00:00Z",
            "amount": "100.00",
            "source_type": "MANUAL",
        },
    )
    assert response.status_code == 403


def test_ingest_blockchain_balance_endpoint():
    wallet_id = seed_wallet_via_api("0xapi-bal-ingest")
    response = client.post(
        f"/crypto/ingestion/blockchain-balances/{wallet_id}?token_symbol=ETH",
        headers=auth_headers(),
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["wallet_id"] == wallet_id
    assert data["token_symbol"] == "ETH"
