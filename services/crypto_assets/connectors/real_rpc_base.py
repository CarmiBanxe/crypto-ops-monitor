"""Production-ready RPC connector interfaces. Replace mock bodies with real HTTP clients when credentials are provisioned."""
from decimal import Decimal
from services.crypto_assets.connectors.blockchain_base import BlockchainConnector


class RealEthereumRPCConnector(BlockchainConnector):
    network_code = "ethereum"

    def __init__(self, rpc_url: str | None = None, api_key: str | None = None):
        self.rpc_url = rpc_url
        self.api_key = api_key

    def fetch_balance(self, address: str, token_symbol: str) -> Decimal:
        # TODO: replace with web3.py eth_getBalance call
        if not self.rpc_url:
            return Decimal("0")
        return Decimal("0")

    def fetch_transactions(self, address: str, since: str | None = None) -> list[dict]:
        # TODO: replace with Etherscan/Alchemy API pagination
        return []


class RealBitcoinRPCConnector(BlockchainConnector):
    network_code = "bitcoin"

    def __init__(self, rpc_url: str | None = None, api_key: str | None = None):
        self.rpc_url = rpc_url
        self.api_key = api_key

    def fetch_balance(self, address: str, token_symbol: str) -> Decimal:
        if not self.rpc_url:
            return Decimal("0")
        return Decimal("0")

    def fetch_transactions(self, address: str, since: str | None = None) -> list[dict]:
        return []
