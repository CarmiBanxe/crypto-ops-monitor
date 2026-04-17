import csv
import io
from decimal import Decimal
from services.crypto_assets.models import CanonicalTransaction


class ExportService:
    HEADERS = [
        "id", "tx_datetime", "direction", "amount", "token_symbol",
        "tx_hash", "internal_wallet_id", "external_wallet",
        "counterparty_id", "source_type", "notes",
    ]

    @staticmethod
    def transactions_to_csv(transactions: list[CanonicalTransaction]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(ExportService.HEADERS)
        for tx in transactions:
            writer.writerow([
                tx.id,
                tx.tx_datetime,
                tx.direction.value if tx.direction else "",
                format(tx.amount, "f") if isinstance(tx.amount, Decimal) else str(tx.amount),
                tx.token_symbol,
                tx.tx_hash,
                tx.internal_wallet_id or "",
                tx.external_wallet or "",
                tx.counterparty_id or "",
                tx.source_type.value if tx.source_type else "",
                tx.notes or "",
            ])
        return output.getvalue()

    @staticmethod
    def transactions_to_tsv(transactions: list[CanonicalTransaction]) -> str:
        output = io.StringIO()
        writer = csv.writer(output, delimiter="\t")
        writer.writerow(ExportService.HEADERS)
        for tx in transactions:
            writer.writerow([
                tx.id,
                tx.tx_datetime,
                tx.direction.value if tx.direction else "",
                format(tx.amount, "f") if isinstance(tx.amount, Decimal) else str(tx.amount),
                tx.token_symbol,
                tx.tx_hash,
                tx.internal_wallet_id or "",
                tx.external_wallet or "",
                tx.counterparty_id or "",
                tx.source_type.value if tx.source_type else "",
                tx.notes or "",
            ])
        return output.getvalue()
