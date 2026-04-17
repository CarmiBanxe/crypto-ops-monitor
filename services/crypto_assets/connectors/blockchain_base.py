from abc import ABC, abstractmethod
from decimal import Decimal


class BlockchainConnector(ABC):
    network_code: str = ""

    @abstractmethod
    def fetch_balance(self, address: str, token_symbol: str) -> Decimal:
        ...

    @abstractmethod
    def fetch_transactions(self, address: str, since: str | None = None) -> list[dict]:
        ...
