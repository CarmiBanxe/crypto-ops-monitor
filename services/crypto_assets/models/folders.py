from sqlalchemy import String, ForeignKey, Index, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class WalletFolder(TimestampMixin, Base):
    __tablename__ = "crypto_wallet_folders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("crypto_wallet_folders.id"),
        nullable=True,
    )
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)


class WalletFolderLink(TimestampMixin, Base):
    __tablename__ = "crypto_wallet_folder_links"
    __table_args__ = (
        UniqueConstraint("folder_id", "wallet_id", name="uq_folder_wallet_link"),
        Index("ix_crypto_wallet_folder_links_folder_id", "folder_id"),
        Index("ix_crypto_wallet_folder_links_wallet_id", "wallet_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    folder_id: Mapped[int] = mapped_column(
        ForeignKey("crypto_wallet_folders.id"),
        nullable=False,
    )
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("crypto_wallets.id"),
        nullable=False,
    )


class WalletTag(TimestampMixin, Base):
    __tablename__ = "crypto_wallet_tags"
    __table_args__ = (
        Index("ix_crypto_wallet_tags_wallet_id", "wallet_id"),
        Index("ix_crypto_wallet_tags_tag", "tag"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("crypto_wallets.id"),
        nullable=False,
    )
    tag: Mapped[str] = mapped_column(String(120), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)


class ApprovalRequest(TimestampMixin, Base):
    __tablename__ = "crypto_approval_requests"
    __table_args__ = (
        Index("ix_crypto_approval_requests_status", "status"),
        Index("ix_crypto_approval_requests_object_type", "object_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    action_type: Mapped[str] = mapped_column(String(120), nullable=False)
    object_type: Mapped[str] = mapped_column(String(120), nullable=False)
    object_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="PENDING")
    initiator: Mapped[str] = mapped_column(String(120), nullable=False)
    approver: Mapped[str | None] = mapped_column(String(120), nullable=True)
