import services.crypto_assets.db as db_mod
from services.crypto_assets.models import Network, WalletSourceType, WalletType
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.repositories.ingestion_repository import IngestionRunRepository
from services.crypto_assets.service.wallet_service import WalletService
from services.crypto_assets.service.ingestion_service import IngestionService
from services.crypto_assets.schemas.wallets import WalletCreate


def seed_ethereum(db):
    network = db.query(Network).filter_by(identifier="ethereum").first()
    if network is None:
        network = Network(name="Ethereum", identifier="ethereum")
        db.add(network)
        db.commit()
        db.refresh(network)
    return network


def test_wallet_service_create_and_list():
    db = db_mod.SessionLocal()
    try:
        network = seed_ethereum(db)
        service = WalletService(WalletRepository(db))
        wallet = service.create_wallet(
            WalletCreate(
                address="0x111",
                display_name="Test Wallet",
                network_id=network.id,
                source_type=WalletSourceType.MANUAL,
                source_ref="manual-1",
                wallet_type=WalletType.NON_CUSTODY,
            )
        )
        assert wallet.id is not None
        assert any(w.address == "0x111" for w in service.list_wallets())
    finally:
        db.close()


def test_mock_ailink_sync_creates_wallets():
    db = db_mod.SessionLocal()
    try:
        network = seed_ethereum(db)
        service = IngestionService(
            ingestion_repo=IngestionRunRepository(db),
            wallet_repo=WalletRepository(db),
        )
        run = service.run_ailink_wallet_sync()
        assert run.status.value == "SUCCEEDED"
        assert run.stats_json["created"] >= 1
    finally:
        db.close()


def test_mock_ailink_sync_is_idempotent():
    db = db_mod.SessionLocal()
    try:
        network = seed_ethereum(db)
        service = IngestionService(
            ingestion_repo=IngestionRunRepository(db),
            wallet_repo=WalletRepository(db),
        )
        run1 = service.run_ailink_wallet_sync()
        run2 = service.run_ailink_wallet_sync()
        assert run1.stats_json["created"] >= 1
        assert run2.stats_json["created"] == 0
        assert run2.stats_json["updated"] >= 1
    finally:
        db.close()
