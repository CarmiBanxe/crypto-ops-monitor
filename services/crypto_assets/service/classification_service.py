from sqlalchemy import select
from sqlalchemy.orm import Session
from services.crypto_assets.models import ClassificationRule, CanonicalTransaction


class ClassificationService:
    def __init__(self, db: Session):
        self.db = db

    def add_rule(self, rule: ClassificationRule) -> ClassificationRule:
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def list_rules(self) -> list[ClassificationRule]:
        stmt = select(ClassificationRule).order_by(ClassificationRule.priority.asc())
        return list(self.db.scalars(stmt).all())

    def classify(self, tx: CanonicalTransaction) -> str | None:
        rules = self.list_rules()
        for rule in rules:
            if rule.token_symbol and rule.token_symbol != tx.token_symbol:
                continue
            if rule.direction and rule.direction != tx.direction.value:
                continue
            return rule.account_code
        return None
