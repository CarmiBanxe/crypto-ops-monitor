from sqlalchemy import select
from sqlalchemy.orm import Session

from services.crypto_assets.models import CounterpartyWalletLink


class CounterpartyWalletLinkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, entity: CounterpartyWalletLink) -> CounterpartyWalletLink:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def list_all(self) -> list[CounterpartyWalletLink]:
        stmt = select(CounterpartyWalletLink).order_by(CounterpartyWalletLink.id.desc())
        return list(self.db.scalars(stmt).all())

    def find(self, counterparty_id: int, wallet_id: int) -> CounterpartyWalletLink | None:
        stmt = select(CounterpartyWalletLink).where(
            CounterpartyWalletLink.counterparty_id == counterparty_id,
            CounterpartyWalletLink.wallet_id == wallet_id,
        )
        return self.db.scalars(stmt).first()

    def find_by_counterparty(self, counterparty_id: int) -> list[CounterpartyWalletLink]:
        stmt = select(CounterpartyWalletLink).where(
            CounterpartyWalletLink.counterparty_id == counterparty_id
        ).order_by(CounterpartyWalletLink.id.desc())
        return list(self.db.scalars(stmt).all())

    def delete(self, entity: CounterpartyWalletLink) -> None:
        self.db.delete(entity)
        self.db.commit()
