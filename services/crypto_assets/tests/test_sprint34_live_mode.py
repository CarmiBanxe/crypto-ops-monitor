from services.crypto_assets.connectors.mock_bitcoin import MockBitcoinConnector
from services.crypto_assets.connectors.mock_ethereum import MockEthereumConnector
from services.crypto_assets.connectors.real_rpc_base import (
    RealBitcoinRPCConnector,
    RealEthereumRPCConnector,
)
from services.crypto_assets.service.source_registry import SourceRegistry


def test_live_mode_defaults_to_mock_when_unset(monkeypatch):
    monkeypatch.delenv("LIVE_MODE", raising=False)
    registry = SourceRegistry()
    assert isinstance(registry.get_blockchain_connector("ethereum"), MockEthereumConnector)
    assert isinstance(registry.get_blockchain_connector("bitcoin"), MockBitcoinConnector)


def test_live_mode_false_uses_mock_connectors(monkeypatch):
    monkeypatch.setenv("LIVE_MODE", "false")
    registry = SourceRegistry()
    assert isinstance(registry.get_blockchain_connector("ethereum"), MockEthereumConnector)
    assert isinstance(registry.get_blockchain_connector("bitcoin"), MockBitcoinConnector)


def test_live_mode_true_uses_real_connectors_for_supported_networks(monkeypatch):
    monkeypatch.setenv("LIVE_MODE", "true")
    registry = SourceRegistry()
    assert isinstance(registry.get_blockchain_connector("ethereum"), RealEthereumRPCConnector)
    assert isinstance(registry.get_blockchain_connector("bitcoin"), RealBitcoinRPCConnector)
