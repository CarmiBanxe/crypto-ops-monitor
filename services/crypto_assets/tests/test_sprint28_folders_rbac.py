import services.crypto_assets.db as db_mod
from fastapi.testclient import TestClient
from api.main import app
from services.crypto_assets.models import Network, WalletSourceType, WalletType
from services.crypto_assets.models.folders import WalletFolder, WalletFolderLink, WalletTag, ApprovalRequest
from services.crypto_assets.repositories.folder_repository import FolderRepository
from services.crypto_assets.repositories.approval_repository import ApprovalRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.schemas.wallets import WalletCreate
from services.crypto_assets.service.wallet_service import WalletService

client = TestClient(app)


def auth_headers(token: str = "finance-director-token") -> dict:
    return {"Authorization": f"Bearer {token}"}


def ops_headers() -> dict:
    return {"Authorization": "Bearer operations-token"}


def seed(db):
    network = db.query(Network).filter_by(identifier="ethereum").first()
    if network is None:
        network = Network(name="Ethereum", identifier="ethereum")
        db.add(network)
        db.commit()
        db.refresh(network)
    return network
    network = Network(name="Ethereum", identifier="ethereum")
    db.add(network)
    db.commit()
    db.refresh(network)
    return network


def test_folder_create_and_wallet_assignment():
    db = db_mod.SessionLocal()
    try:
        network = seed(db)
        wallet_svc = WalletService(WalletRepository(db))
        wallet = wallet_svc.create_wallet(WalletCreate(
            address="0xfolder01",
            display_name="Folder Wallet",
            network_id=network.id,
            source_type=WalletSourceType.MANUAL,
            wallet_type=WalletType.NON_CUSTODY,
        ))

        repo = FolderRepository(db)
        folder = repo.create_folder(WalletFolder(name="Hot Wallets", created_by="lidia"))
        assert folder.id is not None

        link = repo.add_wallet_to_folder(WalletFolderLink(
            folder_id=folder.id, wallet_id=wallet.id,
        ))
        assert link.id is not None

        wallet_ids = repo.list_wallets_in_folder(folder.id)
        assert wallet.id in wallet_ids
    finally:
        db.close()


def test_wallet_tags():
    db = db_mod.SessionLocal()
    try:
        network = seed(db)
        wallet_svc = WalletService(WalletRepository(db))
        wallet = wallet_svc.create_wallet(WalletCreate(
            address="0xtag01",
            display_name="Tag Wallet",
            network_id=network.id,
            source_type=WalletSourceType.MANUAL,
            wallet_type=WalletType.NON_CUSTODY,
        ))

        repo = FolderRepository(db)
        tag = repo.create_wallet_tag(WalletTag(
            wallet_id=wallet.id, tag="REVIEW_NEEDED", author="sasha",
        ))
        assert tag.id is not None

        tags = repo.list_tags_for_wallet(wallet.id)
        assert len(tags) == 1
        assert tags[0].tag == "REVIEW_NEEDED"
    finally:
        db.close()


def test_approval_request_lifecycle():
    db = db_mod.SessionLocal()
    try:
        repo = ApprovalRepository(db)
        req = repo.create(ApprovalRequest(
            action_type="DELETE_WALLET",
            object_type="wallet",
            object_ref="42",
            payload_json='{"reason": "duplicate"}',
            status="PENDING",
            initiator="anton",
        ))
        assert req.id is not None
        assert req.status == "PENDING"

        pending = repo.list_pending()
        assert any(r.id == req.id for r in pending)

        req.status = "APPROVED"
        req.approver = "lidia"
        updated = repo.update(req)
        assert updated.status == "APPROVED"
        assert updated.approver == "lidia"
    finally:
        db.close()


def test_rbac_operations_cannot_create_wallet():
    response = client.post(
        "/crypto/wallets",
        headers=ops_headers(),
        json={
            "address": "0xrbac01",
            "display_name": "RBAC Test",
            "network_id": 1,
            "source_type": "MANUAL",
            "wallet_type": "NON_CUSTODY",
        },
    )
    assert response.status_code == 403


def test_rbac_operations_can_read_wallets():
    response = client.get("/crypto/wallets", headers=ops_headers())
    assert response.status_code == 200
