from sqlalchemy import select
from sqlalchemy.orm import Session

from services.crypto_assets.models import IngestionRun


class IngestionRunRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, run: IngestionRun) -> IngestionRun:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get(self, run_id: int) -> IngestionRun | None:
        return self.db.get(IngestionRun, run_id)

    def list(self) -> list[IngestionRun]:
        return list(self.db.scalars(select(IngestionRun).order_by(IngestionRun.id.desc())).all())

    def update(self, run: IngestionRun) -> IngestionRun:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run
