from sqlalchemy import select
from sqlalchemy.orm import Session

from services.crypto_assets.models.comments import TransactionComment, TransactionTag


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, entity: TransactionComment) -> TransactionComment:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def create_comment(self, entity: TransactionComment) -> TransactionComment:
        return self.create(entity)

    def create_tag(self, entity: TransactionTag) -> TransactionTag:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def list_by_transaction(self, transaction_id: int) -> list[TransactionComment]:
        stmt = (
            select(TransactionComment)
            .where(TransactionComment.transaction_id == transaction_id)
            .order_by(TransactionComment.id.asc())
        )
        return list(self.db.scalars(stmt).all())

    def list_tags_by_transaction(self, transaction_id: int) -> list[TransactionTag]:
        stmt = (
            select(TransactionTag)
            .where(TransactionTag.transaction_id == transaction_id)
            .order_by(TransactionTag.id.asc())
        )
        return list(self.db.scalars(stmt).all())
