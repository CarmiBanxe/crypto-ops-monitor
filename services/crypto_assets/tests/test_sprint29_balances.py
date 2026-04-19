from decimal import Decimal

import services.crypto_assets.db as db_mod
from services.crypto_assets.connectors.mock_ethereum import MockEthereumConnector
from services.crypto_assets.models import (
    Network,
    Wallet,
    WalletSourceType,
    WalletType,
)
from services.crypto_assets.repositories.balance_repository import BalanceRepository
from services.crypto_assets.service.balance_service import BalanceService


def get_or_create_network(db, identifier="ethereum", name="Ethereum"):
    network = db.query(Network).filter_by(identifier=identifier).first()
    if not network:
        network = Network(name=name, identifier=identifier)
        db.add(network)
        db.commit()
        db.refresh(network)
    return network


def seed_wallet(db, address):
    network = get_or_create_network(db)
    existing = db.query(Wallet).filter_by(
        network_id=network.id, address=address
    ).first()
    if existing:
        return existing
    wallet = Wallet(
        address=address,
        display_name="Balance Wallet",
        network_id=network.id,
        source_type=WalletSourceType.MANUAL,
        wallet_type=WalletType.NON_CUSTODY,
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def test_balance_snapshot_create_and_latest():
    db = db_mod.SessionLocal()
    try:
        wallet = seed_wallet(db, "0xbal001")
        service = BalanceService(BalanceRepository(db))

        service.record_snapshot(
            wallet_id=wallet.id,
            token_symbol="USDC",
            amount=Decimal("1000.50"),
            source_type=WalletSourceType.MANUAL,
            observed_at="2026-04-17T10:00:00Z",
        )
        service.record_snapshot(
            wallet_id=wallet.id,
            token_symbol="USDC",
            amount=Decimal("1500.75"),
            source_type=WalletSourceType.MANUAL,
            observed_at="2026-04-17T12:00:00Z",
        )

        current = service.get_current_balance(wallet.id, "USDC")
        assert current == Decimal("1500.75")

        balances = service.list_wallet_balances(wallet.id)
        assert len(balances) >= 2
    finally:
        db.close()


def test_mock_ethereum_connector():
    connector = MockEthereumConnector(balances={
        "0xabc": {"ETH": Decimal("2.5"), "USDC": Decimal("500")},
    })
    assert connector.network_code == "ethereum"
    assert connector.fetch_balance("0xabc", "ETH") == Decimal("2.5")
    assert connector.fetch_balance("0xabc", "USDC") == Decimal("500")
    assert connector.fetch_balance("0xunknown", "ETH") == Decimal("0")
    assert connector.fetch_transactions("0xabc") == []


def test_blockchain_connector_to_balance_snapshot_flow():
    db = db_mod.SessionLocal()
    try:
        wallet = seed_wallet(db, "0xbal002")
        connector = MockEthereumConnector(balances={
            wallet.address: {"ETH": Decimal("3.14159")},
        })
        service = BalanceService(BalanceRepository(db))

        amount = connector.fetch_balance(wallet.address, "ETH")
        snapshot = service.record_snapshot(
            wallet_id=wallet.id,
            token_symbol="ETH",
            amount=amount,
            source_type=WalletSourceType.MANUAL,
            observed_at="2026-04-17T14:00:00Z",
        )
        assert snapshot.amount.quantize(Decimal("0.00001")) == Decimal("3.14159")
        assert service.get_current_balance(wallet.id, "ETH").quantize(Decimal("0.00001")) == Decimal("3.14159")
    finally:
        db.close()
