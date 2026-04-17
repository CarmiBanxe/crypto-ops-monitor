from fastapi.testclient import TestClient

from api.main import app
from services.crypto_assets.audit import AUDIT_LOG

client = TestClient(app)


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_operations_cannot_create_counterparty():
    response = client.post(
        "/crypto/counterparties",
        headers=auth_headers("operations-token"),
        json={"name": "Blocked CP"},
    )
    assert response.status_code == 403


def test_counterparty_crud_and_link_via_api():
    AUDIT_LOG.clear()

    wallet_response = client.post(
        "/crypto/wallets",
        headers=auth_headers("finance-director-token"),
        json={
            "address": "0xapi001",
            "display_name": "API Counterparty Wallet",
            "network_id": 1,
            "source_type": "MANUAL",
            "source_ref": "api-wallet-1",
            "wallet_type": "NON_CUSTODY",
            "status": "ACTIVE",
        },
    )
    assert wallet_response.status_code == 200, wallet_response.text
    wallet_id = wallet_response.json()["id"]

    create_response = client.post(
        "/crypto/counterparties",
        headers=auth_headers("head-payments-token"),
        json={
            "name": "Stillman",
            "risk_class": "MEDIUM",
            "properties_json": {"source": "api-test"},
            "status": "ACTIVE",
        },
    )
    assert create_response.status_code == 200, create_response.text
    counterparty_id = create_response.json()["id"]

    get_response = client.get(
        f"/crypto/counterparties/{counterparty_id}",
        headers=auth_headers("operations-token"),
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Stillman"

    update_response = client.put(
        f"/crypto/counterparties/{counterparty_id}",
        headers=auth_headers("finance-director-token"),
        json={"risk_class": "HIGH"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["risk_class"] == "HIGH"

    link_response = client.post(
        "/crypto/counterparty-wallet-links",
        headers=auth_headers("finance-director-token"),
        json={
            "counterparty_id": counterparty_id,
            "wallet_id": wallet_id,
        },
    )
    assert link_response.status_code == 200, link_response.text
    assert link_response.json()["wallet_id"] == wallet_id

    list_links = client.get(
        "/crypto/counterparty-wallet-links",
        headers=auth_headers("operations-token"),
    )
    assert list_links.status_code == 200
    assert any(item["wallet_id"] == wallet_id for item in list_links.json())

    delete_response = client.delete(
        f"/crypto/counterparties/{counterparty_id}",
        headers=auth_headers("finance-director-token"),
    )
    assert delete_response.status_code == 204

    actions = [entry["action"] for entry in AUDIT_LOG]
    assert "CREATE_COUNTERPARTY" in actions
    assert "UPDATE_COUNTERPARTY" in actions
    assert "LINK_COUNTERPARTY_WALLET" in actions
    assert "DELETE_COUNTERPARTY" in actions
