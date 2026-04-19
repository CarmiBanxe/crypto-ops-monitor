from sqlalchemy import select
from sqlalchemy.orm import Session

from services.crypto_assets.models import CanonicalTransaction


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, tx: CanonicalTransaction) -> CanonicalTransaction:
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def get(self, tx_id: int) -> CanonicalTransaction | None:
        return self.db.get(CanonicalTransaction, tx_id)

    def list(self) -> list[CanonicalTransaction]:
        stmt = select(CanonicalTransaction).order_by(CanonicalTransaction.id.desc())
        return list(self.db.scalars(stmt).all())
