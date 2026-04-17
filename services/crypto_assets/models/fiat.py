from decimal import Decimal
from sqlalchemy import String, Numeric, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin


class FiatRate(TimestampMixin, Base):
    __tablename__ = "crypto_fiat_rates"
    __table_args__ = (
        UniqueConstraint("token_symbol", "fiat_currency", "observed_at", name="uq_fiat_rate"),
        Index("ix_crypto_fiat_rates_token_fiat", "token_symbol", "fiat_currency"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token_symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    fiat_currency: Mapped[str] = mapped_column(String(10), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    observed_at: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(120), nullable=False)


class XeroPosting(TimestampMixin, Base):
    __tablename__ = "crypto_xero_postings"
    __table_args__ = (
        Index("ix_crypto_xero_postings_tx_id", "transaction_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(nullable=False)
    account_code: Mapped[str] = mapped_column(String(64), nullable=False)
    debit_amount: Mapped[Decimal | None] = mapped_column(Numeric(36, 18), nullable=True)
    credit_amount: Mapped[Decimal | None] = mapped_column(Numeric(36, 18), nullable=True)
    fiat_currency: Mapped[str] = mapped_column(String(10), nullable=False)
    fiat_amount: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    status: Mapped[str] = mapped_column(String(60), nullable=False, default="PENDING")
    xero_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ClassificationRule(TimestampMixin, Base):
    __tablename__ = "crypto_classification_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    network: Mapped[str | None] = mapped_column(String(120), nullable=True)
    token_symbol: Mapped[str | None] = mapped_column(String(64), nullable=True)
    direction: Mapped[str | None] = mapped_column(String(20), nullable=True)
    wallet_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    account_code: Mapped[str] = mapped_column(String(64), nullable=False)
    priority: Mapped[int] = mapped_column(nullable=False, default=100)


class FrozenReport(TimestampMixin, Base):
    __tablename__ = "crypto_frozen_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(60), nullable=False)
    period_from: Mapped[str] = mapped_column(String(64), nullable=False)
    period_to: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[str] = mapped_column(String, nullable=False)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)


class TravelRuleRecord(TimestampMixin, Base):
    __tablename__ = "crypto_travel_rule_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(nullable=False)
    originator_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    originator_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    beneficiary_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    beneficiary_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vasp_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(60), nullable=False, default="PENDING")
