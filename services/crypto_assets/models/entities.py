from decimal import Decimal

from sqlalchemy import (
    JSON,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin
from .enums import (
    CounterpartyKind,
    Direction,
    IngestionStatus,
    IngestionTriggerType,
    RecordStatus,
    WalletSourceType,
    WalletType,
)


class Network(TimestampMixin, Base):
    __tablename__ = "crypto_networks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    identifier: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    wallets: Mapped[list["Wallet"]] = relationship(back_populates="network")


class Wallet(TimestampMixin, Base):
    __tablename__ = "crypto_wallets"
    __table_args__ = (
        UniqueConstraint("network_id", "address", name="uq_crypto_wallet_network_address"),
        Index("ix_crypto_wallets_display_name", "display_name"),
        Index("ix_crypto_wallets_address", "address"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    network_id: Mapped[int] = mapped_column(ForeignKey("crypto_networks.id"), nullable=False)
    source_type: Mapped[WalletSourceType] = mapped_column(Enum(WalletSourceType), nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    wallet_type: Mapped[WalletType] = mapped_column(
        Enum(WalletType), nullable=False, default=WalletType.UNKNOWN
    )
    status: Mapped[RecordStatus] = mapped_column(
        Enum(RecordStatus), nullable=False, default=RecordStatus.ACTIVE
    )

    network: Mapped["Network"] = relationship(back_populates="wallets")
    counterparty_links: Mapped[list["CounterpartyWalletLink"]] = relationship(
        back_populates="wallet"
    )
    balance_snapshots: Mapped[list["WalletBalanceSnapshot"]] = relationship(
        back_populates="wallet"
    )


class Counterparty(TimestampMixin, Base):
    __tablename__ = "crypto_counterparties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[CounterpartyKind] = mapped_column(
        Enum(CounterpartyKind), nullable=False, default=CounterpartyKind.UNKNOWN
    )
    risk_class: Mapped[str | None] = mapped_column(String(120), nullable=True)
    properties_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[RecordStatus] = mapped_column(
        Enum(RecordStatus), nullable=False, default=RecordStatus.ACTIVE
    )

    wallet_links: Mapped[list["CounterpartyWalletLink"]] = relationship(
        back_populates="counterparty"
    )


class CounterpartyWalletLink(TimestampMixin, Base):
    __tablename__ = "crypto_counterparty_wallet_links"
    __table_args__ = (
        UniqueConstraint("counterparty_id", "wallet_id", name="uq_counterparty_wallet_link"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    counterparty_id: Mapped[int] = mapped_column(
        ForeignKey("crypto_counterparties.id"), nullable=False
    )
    wallet_id: Mapped[int] = mapped_column(ForeignKey("crypto_wallets.id"), nullable=False)

    counterparty: Mapped["Counterparty"] = relationship(back_populates="wallet_links")
    wallet: Mapped["Wallet"] = relationship(back_populates="counterparty_links")


class SourceAccount(TimestampMixin, Base):
    __tablename__ = "crypto_source_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_type: Mapped[WalletSourceType] = mapped_column(Enum(WalletSourceType), nullable=False)
    account_ref: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[RecordStatus] = mapped_column(
        Enum(RecordStatus), nullable=False, default=RecordStatus.ACTIVE
    )


class IngestionRun(TimestampMixin, Base):
    __tablename__ = "crypto_ingestion_runs"
    __table_args__ = (
        Index("ix_crypto_ingestion_runs_connector_type", "connector_type"),
        Index("ix_crypto_ingestion_runs_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    connector_type: Mapped[str] = mapped_column(String(120), nullable=False)
    trigger_type: Mapped[IngestionTriggerType] = mapped_column(
        Enum(IngestionTriggerType), nullable=False
    )
    status: Mapped[IngestionStatus] = mapped_column(Enum(IngestionStatus), nullable=False)
    stats_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class RawTransactionEvent(TimestampMixin, Base):
    __tablename__ = "crypto_raw_transaction_events"
    __table_args__ = (
        UniqueConstraint("source_type", "source_fingerprint", name="uq_raw_event_fingerprint"),
        Index("ix_crypto_raw_transaction_events_occurred_at", "occurred_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ingestion_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("crypto_ingestion_runs.id"), nullable=True
    )
    source_type: Mapped[WalletSourceType] = mapped_column(Enum(WalletSourceType), nullable=False)
    source_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False)
    occurred_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)


class CanonicalTransaction(TimestampMixin, Base):
    __tablename__ = "crypto_canonical_transactions"
    __table_args__ = (
        Index("ix_crypto_canonical_transactions_tx_datetime", "tx_datetime"),
        Index("ix_crypto_canonical_transactions_token_symbol", "token_symbol"),
        Index("ix_crypto_canonical_transactions_tx_hash", "tx_hash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tx_datetime: Mapped[str] = mapped_column(String(64), nullable=False)
    direction: Mapped[Direction] = mapped_column(Enum(Direction), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    token_symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    tx_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    internal_wallet_id: Mapped[int | None] = mapped_column(
        ForeignKey("crypto_wallets.id"), nullable=True
    )
    external_wallet: Mapped[str | None] = mapped_column(String(255), nullable=True)
    counterparty_id: Mapped[int | None] = mapped_column(
        ForeignKey("crypto_counterparties.id"), nullable=True
    )
    source_type: Mapped[WalletSourceType] = mapped_column(Enum(WalletSourceType), nullable=False)
    raw_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("crypto_raw_transaction_events.id"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class WalletBalanceSnapshot(TimestampMixin, Base):
    __tablename__ = "crypto_wallet_balance_snapshots"
    __table_args__ = (
        Index("ix_crypto_wallet_balance_snapshots_observed_at", "observed_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("crypto_wallets.id"), nullable=False)
    token_symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    observed_at: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    source_type: Mapped[WalletSourceType] = mapped_column(Enum(WalletSourceType), nullable=False)

    wallet: Mapped["Wallet"] = relationship(back_populates="balance_snapshots")
