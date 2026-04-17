from decimal import Decimal
import services.crypto_assets.db as db_mod
from services.crypto_assets.models import (
    Network, Wallet, WalletSourceType, WalletType,
)
from services.crypto_assets.repositories.balance_repository import BalanceRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.service.balance_service import BalanceService
from services.crypto_assets.service.reconciliation_service import ReconciliationService


def get_or_create_network(db, identifier="ethereum", name="Ethereum"):
    n = db.query(Network).filter_by(identifier=identifier).first()
    if not n:
        n = Network(name=name, identifier=identifier)
        db.add(n)
        db.commit()
        db.refresh(n)
    return n


def seed_wallet(db, address):
    net = get_or_create_network(db)
    w = db.query(Wallet).filter_by(network_id=net.id, address=address).first()
    if w:
        return w
    w = Wallet(
        address=address, display_name="Sprint 31 Wallet",
        network_id=net.id, source_type=WalletSourceType.MANUAL,
        wallet_type=WalletType.NON_CUSTODY,
    )
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def test_reconciliation_ok_and_mismatch():
    db = db_mod.SessionLocal()
    try:
        wallet = seed_wallet(db, "0xrec001")
        bal_service = BalanceService(BalanceRepository(db))
        bal_service.record_snapshot(
            wallet_id=wallet.id, token_symbol="USDC",
            amount=Decimal("1000.00"), source_type=WalletSourceType.MANUAL,
            observed_at="2026-04-17T22:00:00Z",
        )
        rec = ReconciliationService(BalanceRepository(db), WalletRepository(db))
        ok = rec.check_wallet(wallet.id, "USDC", Decimal("1000.00"))
        assert ok["status"] == "OK"
        mismatch = rec.check_wallet(wallet.id, "USDC", Decimal("500.00"))
        assert mismatch["status"] == "MISMATCH"
        no_data = rec.check_wallet(wallet.id, "BTC", Decimal("1.0"))
        assert no_data["status"] == "NO_DATA"
    finally:
        db.close()


def test_reconciliation_scan_coverage():
    db = db_mod.SessionLocal()
    try:
        seed_wallet(db, "0xrec002")
        rec = ReconciliationService(BalanceRepository(db), WalletRepository(db))
        result = rec.scan_all_wallets("USDC")
        assert "total_wallets" in result
        assert "coverage_pct" in result
    finally:
        db.close()
