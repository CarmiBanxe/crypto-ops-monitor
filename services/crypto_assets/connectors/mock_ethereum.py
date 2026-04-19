from decimal import Decimal

from services.crypto_assets.connectors.blockchain_base import BlockchainConnector


class MockEthereumConnector(BlockchainConnector):
    network_code = "ethereum"

    def __init__(self, balances: dict[str, dict[str, Decimal]] | None = None):
        self._balances = balances or {}

    def fetch_balance(self, address: str, token_symbol: str) -> Decimal:
        return self._balances.get(address, {}).get(token_symbol, Decimal("0"))

    def fetch_transactions(self, address: str, since: str | None = None) -> list[dict]:
        return []
