from sqlalchemy import select
from sqlalchemy.orm import Session

from services.crypto_assets.models import WalletBalanceSnapshot


class BalanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, snapshot: WalletBalanceSnapshot) -> WalletBalanceSnapshot:
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def list_by_wallet(self, wallet_id: int) -> list[WalletBalanceSnapshot]:
        stmt = select(WalletBalanceSnapshot).where(
            WalletBalanceSnapshot.wallet_id == wallet_id
        ).order_by(WalletBalanceSnapshot.observed_at.desc())
        return list(self.db.scalars(stmt).all())

    def latest_for_wallet(self, wallet_id: int, token_symbol: str) -> WalletBalanceSnapshot | None:
        stmt = select(WalletBalanceSnapshot).where(
            WalletBalanceSnapshot.wallet_id == wallet_id,
            WalletBalanceSnapshot.token_symbol == token_symbol,
        ).order_by(WalletBalanceSnapshot.observed_at.desc()).limit(1)
        return self.db.scalars(stmt).first()

    def list_all(self) -> list[WalletBalanceSnapshot]:
        stmt = select(WalletBalanceSnapshot).order_by(
            WalletBalanceSnapshot.observed_at.desc()
        )
        return list(self.db.scalars(stmt).all())
