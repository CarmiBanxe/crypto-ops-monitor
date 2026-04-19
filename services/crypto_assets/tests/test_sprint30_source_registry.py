import pytest

from services.crypto_assets.connectors.mock_binance import MockBinanceAdapter
from services.crypto_assets.connectors.mock_bitcoin import MockBitcoinConnector
from services.crypto_assets.connectors.mock_bsc import MockBSCConnector
from services.crypto_assets.connectors.mock_ethereum import MockEthereumConnector
from services.crypto_assets.connectors.mock_kraken import MockKrakenAdapter
from services.crypto_assets.connectors.mock_overstake import MockOverstakeAdapter
from services.crypto_assets.connectors.mock_polygon import MockPolygonConnector
from services.crypto_assets.service.source_registry import SourceRegistry


def test_registry_resolves_blockchain_connectors():
    registry = SourceRegistry()
    assert isinstance(registry.get_blockchain_connector("ethereum"), MockEthereumConnector)
    assert isinstance(registry.get_blockchain_connector("bitcoin"), MockBitcoinConnector)
    assert isinstance(registry.get_blockchain_connector("polygon"), MockPolygonConnector)
    assert isinstance(registry.get_blockchain_connector("bsc"), MockBSCConnector)


def test_registry_resolves_account_adapters():
    registry = SourceRegistry()
    assert isinstance(registry.get_account_adapter("binance"), MockBinanceAdapter)
    assert isinstance(registry.get_account_adapter("kraken"), MockKrakenAdapter)
    assert isinstance(registry.get_account_adapter("overstake"), MockOverstakeAdapter)


def test_registry_rejects_unknown_sources():
    registry = SourceRegistry()
    with pytest.raises(KeyError):
        registry.get_blockchain_connector("solana")
    with pytest.raises(KeyError):
        registry.get_account_adapter("coinbase")
