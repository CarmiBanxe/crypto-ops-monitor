from decimal import Decimal
from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.orm import Session
from services.crypto_assets.models import FiatRate


class FiatConversionService:
    def __init__(self, db: Session):
        self.db = db

    def record_rate(self, token_symbol: str, fiat_currency: str, rate: Decimal,
                    source: str = "manual", observed_at: str | None = None) -> FiatRate:
        entity = FiatRate(
            token_symbol=token_symbol,
            fiat_currency=fiat_currency,
            rate=rate,
            source=source,
            observed_at=observed_at or datetime.now(UTC).isoformat(),
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def latest_rate(self, token_symbol: str, fiat_currency: str) -> FiatRate | None:
        stmt = select(FiatRate).where(
            FiatRate.token_symbol == token_symbol,
            FiatRate.fiat_currency == fiat_currency,
        ).order_by(FiatRate.observed_at.desc()).limit(1)
        return self.db.scalars(stmt).first()

    def convert(self, amount: Decimal, token_symbol: str, fiat_currency: str) -> Decimal | None:
        rate = self.latest_rate(token_symbol, fiat_currency)
        if rate is None:
            return None
        return (amount * rate.rate).quantize(Decimal("0.01"))
