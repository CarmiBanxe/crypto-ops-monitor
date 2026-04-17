from abc import ABC, abstractmethod
from decimal import Decimal


class ExchangeAdapter(ABC):
    provider_code: str = ""

    @abstractmethod
    def fetch_balances(self, account_ref: str) -> dict[str, Decimal]:
        ...

    @abstractmethod
    def fetch_trades(self, account_ref: str, since: str | None = None) -> list[dict]:
        ...
