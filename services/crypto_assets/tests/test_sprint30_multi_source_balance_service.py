from decimal import Decimal

import services.crypto_assets.db as db_mod
from services.crypto_assets.models import Network, WalletSourceType, WalletType
from services.crypto_assets.repositories.balance_repository import BalanceRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.schemas.wallets import WalletCreate
from services.crypto_assets.service.balance_service import BalanceService
from services.crypto_assets.service.multi_source_balance_service import MultiSourceBalanceService
from services.crypto_assets.service.source_registry import SourceRegistry
from services.crypto_assets.service.wallet_service import WalletService


def seed_wallet(db, address: str):
    network = db.query(Network).filter_by(identifier="ethereum").first()
    if network is None:
        network = Network(name="Ethereum", identifier="ethereum")
        db.add(network)
        db.commit()
        db.refresh(network)
    wallet_service = WalletService(WalletRepository(db))
    return wallet_service.create_wallet(WalletCreate(
        address=address,
        display_name="MS Balance Wallet",
        network_id=network.id,
        source_type=WalletSourceType.MANUAL,
        wallet_type=WalletType.NON_CUSTODY,
    ))


def test_ingest_blockchain_balance():
    db = db_mod.SessionLocal()
    try:
        wallet = seed_wallet(db, "0xms-eth")
        balance_service = BalanceService(BalanceRepository(db))
        registry = SourceRegistry()
        registry.get_blockchain_connector("ethereum")._balances = {
            "0xms-eth": {"ETH": Decimal("1.25")}
        }
        service = MultiSourceBalanceService(balance_service, registry)
        snapshot = service.ingest_blockchain_balance(
            wallet_id=wallet.id,
            network_code="ethereum",
            address="0xms-eth",
            token_symbol="ETH",
        )
        assert snapshot.wallet_id == wallet.id
        assert snapshot.token_symbol == "ETH"
        assert snapshot.amount == Decimal("1.25")
    finally:
        db.close()


def test_ingest_account_balance():
    db = db_mod.SessionLocal()
    try:
        wallet = seed_wallet(db, "0xms-binance")
        balance_service = BalanceService(BalanceRepository(db))
        registry = SourceRegistry()
        registry.get_account_adapter("binance")._balances = {
            "spot": {"BNB": Decimal("8")}
        }
        service = MultiSourceBalanceService(balance_service, registry)
        snapshot = service.ingest_account_balance(
            wallet_id=wallet.id,
            source_code="binance",
            account_id="spot",
            token_symbol="BNB",
        )
        assert snapshot.wallet_id == wallet.id
        assert snapshot.token_symbol == "BNB"
        assert snapshot.amount == Decimal("8")
    finally:
        db.close()
