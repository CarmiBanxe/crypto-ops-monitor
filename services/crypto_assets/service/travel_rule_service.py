from sqlalchemy import select
from sqlalchemy.orm import Session
from services.crypto_assets.models import TravelRuleRecord


class TravelRuleService:
    THRESHOLD_EUR = 1000

    def __init__(self, db: Session):
        self.db = db

    def create_record(self, transaction_id: int, originator_name: str | None = None,
                      originator_address: str | None = None,
                      beneficiary_name: str | None = None,
                      beneficiary_address: str | None = None,
                      vasp_code: str | None = None) -> TravelRuleRecord:
        record = TravelRuleRecord(
            transaction_id=transaction_id,
            originator_name=originator_name,
            originator_address=originator_address,
            beneficiary_name=beneficiary_name,
            beneficiary_address=beneficiary_address,
            vasp_code=vasp_code,
            status="PENDING",
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def mark_submitted(self, record_id: int) -> TravelRuleRecord | None:
        record = self.db.get(TravelRuleRecord, record_id)
        if record is None:
            return None
        record.status = "SUBMITTED"
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_pending(self) -> list[TravelRuleRecord]:
        stmt = select(TravelRuleRecord).where(TravelRuleRecord.status == "PENDING")
        return list(self.db.scalars(stmt).all())
