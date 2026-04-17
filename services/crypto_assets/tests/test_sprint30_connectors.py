from decimal import Decimal

from services.crypto_assets.connectors.mock_binance import MockBinanceAdapter
from services.crypto_assets.connectors.mock_bitcoin import MockBitcoinConnector
from services.crypto_assets.connectors.mock_bsc import MockBSCConnector
from services.crypto_assets.connectors.mock_kraken import MockKrakenAdapter
from services.crypto_assets.connectors.mock_overstake import MockOverstakeAdapter
from services.crypto_assets.connectors.mock_polygon import MockPolygonConnector


def test_bitcoin_connector():
    conn = MockBitcoinConnector(
        balances={"bc1qxyz": {"BTC": Decimal("0.5")}},
        transactions={"bc1qxyz": [{"tx_hash": "btc1", "amount": "0.5"}]},
    )
    assert conn.fetch_balance("bc1qxyz", "BTC") == Decimal("0.5")
    txs = conn.fetch_transactions("bc1qxyz")
    assert len(txs) == 1
    assert txs[0]["tx_hash"] == "btc1"


def test_polygon_connector():
    conn = MockPolygonConnector(
        balances={"0xpoly": {"MATIC": Decimal("25")}},
        transactions={"0xpoly": [{"tx_hash": "poly1", "amount": "25"}]},
    )
    assert conn.fetch_balance("0xpoly", "MATIC") == Decimal("25")
    txs = conn.fetch_transactions("0xpoly")
    assert len(txs) == 1
    assert txs[0]["tx_hash"] == "poly1"


def test_bsc_connector():
    conn = MockBSCConnector(
        balances={"0xbsc": {"BNB": Decimal("7")}},
        transactions={"0xbsc": [{"tx_hash": "bsc1", "amount": "7"}]},
    )
    assert conn.fetch_balance("0xbsc", "BNB") == Decimal("7")
    txs = conn.fetch_transactions("0xbsc")
    assert len(txs) == 1
    assert txs[0]["tx_hash"] == "bsc1"


def test_binance_adapter():
    adapter = MockBinanceAdapter(
        balances={"spot": {"BNB": Decimal("10")}},
        transactions={"spot": [{"id": "bn1", "asset": "BNB", "amount": "10"}]},
    )
    balances = adapter.fetch_account_balances("spot")
    assert balances["BNB"] == Decimal("10")
    txs = adapter.fetch_account_transactions("spot")
    assert len(txs) == 1
    assert txs[0]["id"] == "bn1"


def test_kraken_adapter():
    adapter = MockKrakenAdapter(
        balances={"main": {"ETH": Decimal("3")}},
        transactions={"main": [{"id": "kr1", "asset": "ETH", "amount": "3"}]},
    )
    balances = adapter.fetch_account_balances("main")
    assert balances["ETH"] == Decimal("3")
    txs = adapter.fetch_account_transactions("main")
    assert len(txs) == 1
    assert txs[0]["id"] == "kr1"


def test_overstake_adapter():
    adapter = MockOverstakeAdapter(
        balances={"staking": {"ATOM": Decimal("42")}},
        transactions={"staking": [{"id": "ov1", "asset": "ATOM", "amount": "42"}]},
    )
    balances = adapter.fetch_account_balances("staking")
    assert balances["ATOM"] == Decimal("42")
    txs = adapter.fetch_account_transactions("staking")
    assert len(txs) == 1
    assert txs[0]["id"] == "ov1"
