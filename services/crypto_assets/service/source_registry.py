import os

from services.crypto_assets.connectors.mock_binance import MockBinanceAdapter
from services.crypto_assets.connectors.mock_bitcoin import MockBitcoinConnector
from services.crypto_assets.connectors.mock_bsc import MockBSCConnector
from services.crypto_assets.connectors.mock_ethereum import MockEthereumConnector
from services.crypto_assets.connectors.mock_kraken import MockKrakenAdapter
from services.crypto_assets.connectors.mock_overstake import MockOverstakeAdapter
from services.crypto_assets.connectors.mock_polygon import MockPolygonConnector
from services.crypto_assets.connectors.real_rpc_base import (
    RealBitcoinRPCConnector,
    RealEthereumRPCConnector,
)


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class SourceRegistry:
    def __init__(self):
        live_mode = _env_flag("LIVE_MODE", default=False)

        self._blockchain_classes = {
            "ethereum": RealEthereumRPCConnector if live_mode else MockEthereumConnector,
            "bitcoin": RealBitcoinRPCConnector if live_mode else MockBitcoinConnector,
            "polygon": MockPolygonConnector,
            "bsc": MockBSCConnector,
        }
        self._account_classes = {
            "binance": MockBinanceAdapter,
            "kraken": MockKrakenAdapter,
            "overstake": MockOverstakeAdapter,
        }
        self._blockchain_instances = {}
        self._account_instances = {}

    def register_blockchain_connector(self, network_code: str, connector) -> None:
        self._blockchain_instances[network_code] = connector

    def register_account_adapter(self, source_code: str, adapter) -> None:
        self._account_instances[source_code] = adapter

    def get_blockchain_connector(self, network_code: str):
        if network_code in self._blockchain_instances:
            return self._blockchain_instances[network_code]
        connector_cls = self._blockchain_classes.get(network_code)
        if connector_cls is None:
            raise KeyError(f"Unsupported blockchain network: {network_code}")
        connector = connector_cls()
        self._blockchain_instances[network_code] = connector
        return connector

    def get_account_adapter(self, source_code: str):
        if source_code in self._account_instances:
            return self._account_instances[source_code]
        adapter_cls = self._account_classes.get(source_code)
        if adapter_cls is None:
            raise KeyError(f"Unsupported account source: {source_code}")
        adapter = adapter_cls()
        self._account_instances[source_code] = adapter
        return adapter
