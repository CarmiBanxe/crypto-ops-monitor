import csv
import hashlib
import io
from decimal import Decimal

from services.crypto_assets.models import (
    CanonicalTransaction,
    Direction,
    WalletSourceType,
)
from services.crypto_assets.repositories.transaction_repository import TransactionRepository
from typing import ClassVar


class CSVImportError(Exception):
    pass


class CSVImportService:
    REQUIRED_COLUMNS: ClassVar[list[str]] = [
        "tx_datetime", "direction", "amount", "token_symbol", "tx_hash",
    ]

    def __init__(self, tx_repo: TransactionRepository):
        self.tx_repo = tx_repo

    @staticmethod
    def file_fingerprint(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def row_fingerprint(row: dict) -> str:
        key = f"{row.get('tx_hash','')}-{row.get('tx_datetime','')}-{row.get('token_symbol','')}-{row.get('amount','')}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def import_csv(self, content: str, source_type: WalletSourceType = WalletSourceType.EXCHANGE) -> dict:
        reader = csv.DictReader(io.StringIO(content))
        if not reader.fieldnames:
            raise CSVImportError("CSV has no header")
        missing = [c for c in self.REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise CSVImportError(f"Missing required columns: {missing}")

        imported = 0
        errors = []
        for idx, row in enumerate(reader, start=2):
            try:
                tx = CanonicalTransaction(
                    tx_datetime=row["tx_datetime"],
                    direction=Direction(row["direction"].upper()),
                    amount=Decimal(row["amount"]),
                    token_symbol=row["token_symbol"],
                    tx_hash=row["tx_hash"],
                    external_wallet=row.get("external_wallet") or None,
                    source_type=source_type,
                    notes=row.get("notes") or None,
                )
                self.tx_repo.create(tx)
                imported += 1
            except Exception as e:
                errors.append({"row": idx, "error": str(e)})

        return {
            "imported": imported,
            "errors": errors,
            "file_fingerprint": self.file_fingerprint(content),
        }
