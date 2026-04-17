from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from services.crypto_assets.models import XeroPosting, CanonicalTransaction, Direction
from services.crypto_assets.service.fiat_service import FiatConversionService
from services.crypto_assets.service.classification_service import ClassificationService


class XeroIntegrationService:
    """Mock Xero integration. Real Xero OAuth2 flow would replace the mock_push method."""

    def __init__(self, db: Session, fiat_currency: str = "EUR"):
        self.db = db
        self.fiat_currency = fiat_currency
        self.fiat_service = FiatConversionService(db)
        self.classification = ClassificationService(db)

    def create_posting_for_tx(self, tx: CanonicalTransaction) -> XeroPosting | None:
        fiat_amount = self.fiat_service.convert(tx.amount, tx.token_symbol, self.fiat_currency)
        if fiat_amount is None:
            return None
        account_code = self.classification.classify(tx) or "UNCATEGORIZED"
        posting = XeroPosting(
            transaction_id=tx.id,
            account_code=account_code,
            debit_amount=fiat_amount if tx.direction == Direction.IN else None,
            credit_amount=fiat_amount if tx.direction == Direction.OUT else None,
            fiat_currency=self.fiat_currency,
            fiat_amount=fiat_amount,
            status="PENDING",
        )
        self.db.add(posting)
        self.db.commit()
        self.db.refresh(posting)
        return posting

    def mock_push(self, posting_id: int, xero_ref: str = "XERO-MOCK-001") -> XeroPosting | None:
        posting = self.db.get(XeroPosting, posting_id)
        if posting is None:
            return None
        posting.status = "PUSHED"
        posting.xero_ref = xero_ref
        self.db.add(posting)
        self.db.commit()
        self.db.refresh(posting)
        return posting

    def list_pending(self) -> list[XeroPosting]:
        stmt = select(XeroPosting).where(XeroPosting.status == "PENDING")
        return list(self.db.scalars(stmt).all())
