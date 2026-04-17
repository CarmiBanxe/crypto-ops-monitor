from sqlalchemy import String, ForeignKey, Index, UniqueConstraint
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
