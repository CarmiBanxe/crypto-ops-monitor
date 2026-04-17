from decimal import Decimal


class MockKrakenAdapter:
    source_code = "kraken"

    def __init__(
        self,
        balances: dict[str, dict[str, Decimal]] | None = None,
        transactions: dict[str, list[dict]] | None = None,
    ):
        self._balances = balances or {}
        self._transactions = transactions or {}

    def fetch_account_balances(self, account_id: str) -> dict[str, Decimal]:
        return self._balances.get(account_id, {})

    def fetch_account_transactions(self, account_id: str, since: str | None = None) -> list[dict]:
        return self._transactions.get(account_id, [])
