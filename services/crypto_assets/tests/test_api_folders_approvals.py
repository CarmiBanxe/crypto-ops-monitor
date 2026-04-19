from fastapi.testclient import TestClient

from api.main import app
from services.crypto_assets.audit import AUDIT_LOG
from typing import cast

client = TestClient(app)


def auth_headers(token: str = "finance-director-token") -> dict:
    return {"Authorization": f"Bearer {token}"}


def ops_headers() -> dict:
    return {"Authorization": "Bearer operations-token"}


def ensure_wallet() -> int:
    wallets = client.get("/crypto/wallets", headers=auth_headers()).json()
    if wallets:
        return cast(int, wallets[0]["id"])
    created = client.post(
        "/crypto/wallets",
        headers=auth_headers(),
        json={
            "address": "0xsprint2801",
            "display_name": "Sprint 28 Wallet",
            "network_id": 1,
            "source_type": "MANUAL",
            "wallet_type": "NON_CUSTODY",
        },
    )
    assert created.status_code == 200
    return cast(int, created.json()["id"])


def test_folder_tag_and_approval_api_flow():
    AUDIT_LOG.clear()
    wallet_id = ensure_wallet()

    folder_resp = client.post(
        "/crypto/folders",
        headers=auth_headers(),
        json={"name": "Treasury", "parent_id": None},
    )
    assert folder_resp.status_code == 200
    folder_id = folder_resp.json()["id"]

    link_resp = client.post(
        f"/crypto/folders/{folder_id}/wallets/{wallet_id}",
        headers=auth_headers(),
    )
    assert link_resp.status_code == 201

    tag_resp = client.post(
        f"/crypto/wallets/{wallet_id}/tags",
        headers=auth_headers(),
        json={"tag": "HIGH_VALUE"},
    )
    assert tag_resp.status_code == 200
    assert tag_resp.json()["tag"] == "HIGH_VALUE"

    tags_resp = client.get(f"/crypto/wallets/{wallet_id}/tags", headers=auth_headers())
    assert tags_resp.status_code == 200
    assert any(t["tag"] == "HIGH_VALUE" for t in tags_resp.json())

    approval_resp = client.post(
        "/crypto/approvals",
        headers=auth_headers(),
        json={
            "action_type": "DELETE_WALLET",
            "object_type": "wallet",
            "object_ref": str(wallet_id),
            "payload_json": '{"reason":"duplicate"}',
        },
    )
    assert approval_resp.status_code == 200
    approval_id = approval_resp.json()["id"]

    pending_resp = client.get("/crypto/approvals", headers=auth_headers())
    assert pending_resp.status_code == 200
    assert any(item["id"] == approval_id for item in pending_resp.json())

    approve_resp = client.patch(
        f"/crypto/approvals/{approval_id}",
        headers=auth_headers(),
        json={"status": "APPROVED"},
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "APPROVED"
    assert approve_resp.json()["approver"] == "lidia"

    assert any(item["action"] == "CREATE_WALLET_FOLDER" for item in AUDIT_LOG)
    assert any(item["action"] == "CREATE_WALLET_TAG" for item in AUDIT_LOG)
    assert any(item["action"] == "CREATE_APPROVAL_REQUEST" for item in AUDIT_LOG)
    assert any(item["action"] == "UPDATE_APPROVAL_REQUEST" for item in AUDIT_LOG)


def test_operations_cannot_write_folder_tag_or_approval():
    wallet_id = ensure_wallet()

    folder_resp = client.post(
        "/crypto/folders",
        headers=ops_headers(),
        json={"name": "Ops Forbidden", "parent_id": None},
    )
    assert folder_resp.status_code == 403

    tag_resp = client.post(
        f"/crypto/wallets/{wallet_id}/tags",
        headers=ops_headers(),
        json={"tag": "OPS_TAG"},
    )
    assert tag_resp.status_code == 403

    approval_resp = client.post(
        "/crypto/approvals",
        headers=ops_headers(),
        json={
            "action_type": "DELETE_WALLET",
            "object_type": "wallet",
            "object_ref": str(wallet_id),
        },
    )
    assert approval_resp.status_code == 403
