from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class TransactionComment(TimestampMixin, Base):
    __tablename__ = "crypto_transaction_comments"
    __table_args__ = (
        Index("ix_crypto_tx_comments_transaction_id", "transaction_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("crypto_canonical_transactions.id"), nullable=False
    )
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)


class TransactionTag(TimestampMixin, Base):
    __tablename__ = "crypto_transaction_tags"
    __table_args__ = (
        Index("ix_crypto_tx_tags_transaction_id", "transaction_id"),
        Index("ix_crypto_tx_tags_tag", "tag"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("crypto_canonical_transactions.id"), nullable=False
    )
    tag: Mapped[str] = mapped_column(String(120), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
