from decimal import Decimal

import services.crypto_assets.db as db_mod
from services.crypto_assets.connectors.real_rpc_base import RealBitcoinRPCConnector, RealEthereumRPCConnector
from services.crypto_assets.models import (
    CanonicalTransaction,
    ClassificationRule,
    Direction,
    Network,
    WalletSourceType,
)
from services.crypto_assets.service.classification_service import ClassificationService
from services.crypto_assets.service.fiat_service import FiatConversionService
from services.crypto_assets.service.frozen_report_service import FrozenReportService
from services.crypto_assets.service.travel_rule_service import TravelRuleService
from services.crypto_assets.service.xero_service import XeroIntegrationService


def seed_tx(db, token="USDC", amount="100.00", direction=Direction.IN, tx_hash="0xh-s32"):
    net = db.query(Network).filter_by(identifier="ethereum").first()
    if not net:
        net = Network(name="Ethereum", identifier="ethereum")
        db.add(net)
        db.commit()
        db.refresh(net)
    tx = CanonicalTransaction(
        tx_datetime="2026-04-17T23:00:00Z",
        direction=direction,
        amount=Decimal(amount),
        token_symbol=token,
        tx_hash=tx_hash,
        source_type=WalletSourceType.MANUAL,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def test_fiat_rate_record_and_convert():
    db = db_mod.SessionLocal()
    try:
        service = FiatConversionService(db)
        service.record_rate("USDC", "EUR", Decimal("0.92"), source="test",
                            observed_at="2026-04-17T23:00:00Z")
        result = service.convert(Decimal("100"), "USDC", "EUR")
        assert result == Decimal("92.00")
        assert service.convert(Decimal("10"), "UNKNOWN", "EUR") is None
    finally:
        db.close()


def test_classification_rules_and_match():
    db = db_mod.SessionLocal()
    try:
        service = ClassificationService(db)
        service.add_rule(ClassificationRule(
            token_symbol="USDC", direction="IN",
            account_code="4000", priority=10,
        ))
        tx = seed_tx(db, token="USDC", direction=Direction.IN, tx_hash="0xcls-1")
        assert service.classify(tx) == "4000"
        tx2 = seed_tx(db, token="BTC", direction=Direction.IN, tx_hash="0xcls-2")
        assert service.classify(tx2) is None
    finally:
        db.close()


def test_xero_posting_lifecycle():
    db = db_mod.SessionLocal()
    try:
        FiatConversionService(db).record_rate(
            "USDC", "EUR", Decimal("0.92"), source="test",
            observed_at="2026-04-17T23:00:00Z",
        )
        ClassificationService(db).add_rule(ClassificationRule(
            token_symbol="USDC", direction="IN",
            account_code="4000", priority=10,
        ))
        tx = seed_tx(db, token="USDC", amount="500", direction=Direction.IN, tx_hash="0xxero-1")
        xero = XeroIntegrationService(db, fiat_currency="EUR")
        posting = xero.create_posting_for_tx(tx)
        assert posting is not None
        assert posting.account_code == "4000"
        assert posting.fiat_amount == Decimal("460.00")
        assert posting.status == "PENDING"
        pushed = xero.mock_push(posting.id, xero_ref="XERO-TEST-1")
        assert pushed.status == "PUSHED"
        assert pushed.xero_ref == "XERO-TEST-1"
        assert len(xero.list_pending()) == 0
    finally:
        db.close()


def test_frozen_report_creates_snapshot():
    db = db_mod.SessionLocal()
    try:
        seed_tx(db, tx_hash="0xreport-1")
        service = FrozenReportService(db)
        report = service.create_transaction_report(
            name="Q1 Report",
            period_from="2026-01-01T00:00:00Z",
            period_to="2026-12-31T23:59:59Z",
            created_by="lidia",
        )
        assert report.id is not None
        assert report.name == "Q1 Report"
        payload = service.get_report_payload(report.id)
        assert isinstance(payload, list)
        assert len(payload) >= 1
    finally:
        db.close()


def test_travel_rule_record_lifecycle():
    db = db_mod.SessionLocal()
    try:
        tx = seed_tx(db, tx_hash="0xtravel-1")
        service = TravelRuleService(db)
        rec = service.create_record(
            transaction_id=tx.id,
            originator_name="Alice Corp",
            beneficiary_name="Bob Exchange",
            vasp_code="VASP-001",
        )
        assert rec.status == "PENDING"
        updated = service.mark_submitted(rec.id)
        assert updated.status == "SUBMITTED"
        assert len(service.list_pending()) == 0
    finally:
        db.close()


def test_real_rpc_connectors_are_stub_ready():
    eth = RealEthereumRPCConnector()
    assert eth.network_code == "ethereum"
    assert eth.fetch_balance("0xabc", "ETH") == Decimal("0")
    btc = RealBitcoinRPCConnector()
    assert btc.network_code == "bitcoin"
    assert btc.fetch_balance("bc1q", "BTC") == Decimal("0")
