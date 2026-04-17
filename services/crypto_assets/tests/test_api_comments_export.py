from fastapi.testclient import TestClient

from api.main import app
from services.crypto_assets.audit import AUDIT_LOG

client = TestClient(app)


def auth_headers(token: str = "finance-director-token") -> dict:
    return {"Authorization": f"Bearer {token}"}


def ensure_wallet():
    response = client.post(
        "/crypto/wallets",
        headers=auth_headers(),
        json={
            "address": "0xcomment001",
            "display_name": "Comment Wallet",
            "network_id": 1,
            "source_type": "MANUAL",
            "source_ref": "comment-wallet-1",
            "wallet_type": "NON_CUSTODY",
            "status": "ACTIVE",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_comments_and_export_endpoints():
    AUDIT_LOG.clear()
    ensure_wallet()

    export_response = client.get(
        "/crypto/transactions/export?format=csv",
        headers=auth_headers("operations-token"),
    )
    assert export_response.status_code == 200
    assert "text/csv" in export_response.headers["content-type"]
    assert "tx_hash" in export_response.text

    export_tsv_response = client.get(
        "/crypto/transactions/export?format=tsv",
        headers=auth_headers("operations-token"),
    )
    assert export_tsv_response.status_code == 200
    assert "text/tab-separated-values" in export_tsv_response.headers["content-type"]

    comment_response = client.post(
        "/crypto/transactions/1/comments",
        headers=auth_headers("finance-director-token"),
        json={"transaction_id": 1, "body": "Investigate this transfer"},
    )
    assert comment_response.status_code == 200, comment_response.text
    assert comment_response.json()["body"] == "Investigate this transfer"

    list_response = client.get(
        "/crypto/transactions/1/comments",
        headers=auth_headers("operations-token"),
    )
    assert list_response.status_code == 200
    assert any(item["body"] == "Investigate this transfer" for item in list_response.json())

    actions = [entry["action"] for entry in AUDIT_LOG]
    assert "CREATE_TRANSACTION_COMMENT" in actions
