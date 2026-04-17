from sqlalchemy import select
from sqlalchemy.orm import Session
from services.crypto_assets.models.folders import ApprovalRequest


class ApprovalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, req: ApprovalRequest) -> ApprovalRequest:
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def get(self, req_id: int) -> ApprovalRequest | None:
        return self.db.get(ApprovalRequest, req_id)

    def list_pending(self) -> list[ApprovalRequest]:
        stmt = select(ApprovalRequest).where(
            ApprovalRequest.status == "PENDING"
        ).order_by(ApprovalRequest.id.desc())
        return list(self.db.scalars(stmt).all())

    def update(self, req: ApprovalRequest) -> ApprovalRequest:
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req
