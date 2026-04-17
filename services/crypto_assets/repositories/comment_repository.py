from sqlalchemy import select
from sqlalchemy.orm import Session
from services.crypto_assets.models.comments import TransactionComment, TransactionTag


class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, comment: TransactionComment) -> TransactionComment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def list_by_transaction(self, tx_id: int) -> list[TransactionComment]:
        stmt = select(TransactionComment).where(
            TransactionComment.transaction_id == tx_id
        ).order_by(TransactionComment.id)
        return list(self.db.scalars(stmt).all())

    def create_tag(self, tag: TransactionTag) -> TransactionTag:
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def list_tags_by_transaction(self, tx_id: int) -> list[TransactionTag]:
        stmt = select(TransactionTag).where(
            TransactionTag.transaction_id == tx_id
        ).order_by(TransactionTag.id)
        return list(self.db.scalars(stmt).all())
