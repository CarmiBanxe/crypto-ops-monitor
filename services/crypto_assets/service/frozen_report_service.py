import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.crypto_assets.models import CanonicalTransaction, FrozenReport


class FrozenReportService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction_report(self, name: str, period_from: str, period_to: str,
                                  created_by: str) -> FrozenReport:
        stmt = select(CanonicalTransaction).where(
            CanonicalTransaction.tx_datetime >= period_from,
            CanonicalTransaction.tx_datetime <= period_to,
        )
        txs = list(self.db.scalars(stmt).all())
        payload = [
            {
                "id": tx.id,
                "tx_datetime": tx.tx_datetime,
                "direction": tx.direction.value,
                "amount": str(tx.amount),
                "token_symbol": tx.token_symbol,
                "tx_hash": tx.tx_hash,
            }
            for tx in txs
        ]
        report = FrozenReport(
            name=name,
            report_type="TRANSACTIONS",
            period_from=period_from,
            period_to=period_to,
            payload_json=json.dumps(payload),
            created_by=created_by,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def list_reports(self) -> list[FrozenReport]:
        stmt = select(FrozenReport).order_by(FrozenReport.id.desc())
        return list(self.db.scalars(stmt).all())

    def get_report_payload(self, report_id: int) -> list[dict] | None:
        report = self.db.get(FrozenReport, report_id)
        if report is None:
            return None
        return json.loads(report.payload_json)
