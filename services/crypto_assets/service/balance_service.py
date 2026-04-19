from datetime import UTC, datetime
from decimal import Decimal

from services.crypto_assets.models import WalletBalanceSnapshot, WalletSourceType
from services.crypto_assets.repositories.balance_repository import BalanceRepository


class BalanceService:
    def __init__(self, repo: BalanceRepository):
        self.repo = repo

    def record_snapshot(
        self,
        wallet_id: int,
        token_symbol: str,
        amount: Decimal,
        source_type: WalletSourceType,
        observed_at: str | None = None,
    ) -> WalletBalanceSnapshot:
        snapshot = WalletBalanceSnapshot(
            wallet_id=wallet_id,
            token_symbol=token_symbol,
            amount=amount,
            source_type=source_type,
            observed_at=observed_at or datetime.now(UTC).isoformat(),
        )
        return self.repo.create(snapshot)

    def get_current_balance(self, wallet_id: int, token_symbol: str) -> Decimal | None:
        snapshot = self.repo.latest_for_wallet(wallet_id, token_symbol)
        return snapshot.amount if snapshot else None

    def list_wallet_balances(self, wallet_id: int) -> list[WalletBalanceSnapshot]:
        return self.repo.list_by_wallet(wallet_id)
