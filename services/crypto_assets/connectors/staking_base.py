from abc import ABC, abstractmethod
from decimal import Decimal


class StakingAdapter(ABC):
    provider_code: str = ""

    @abstractmethod
    def fetch_positions(self, account_ref: str) -> list[dict]:
        ...

    @abstractmethod
    def fetch_rewards(self, account_ref: str, since: str | None = None) -> list[dict]:
        ...
