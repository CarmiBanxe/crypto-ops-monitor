import csv
import io
from typing import ClassVar


class ExportService:
    headers: ClassVar[list[str]] = [
        "id",
        "tx_datetime",
        "direction",
        "amount",
        "token_symbol",
        "tx_hash",
        "external_wallet",
        "counterparty_id",
        "source_type",
        "notes",
    ]

    @classmethod
    def transactions_to_csv(cls, transactions) -> str:
        return cls().to_csv(transactions)

    @classmethod
    def transactions_to_tsv(cls, transactions) -> str:
        return cls().to_tsv(transactions)

    def to_csv(self, transactions) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(self.headers)
        for tx in transactions:
            writer.writerow([
                tx.id,
                tx.tx_datetime,
                getattr(tx.direction, "value", tx.direction),
                tx.amount,
                tx.token_symbol,
                tx.tx_hash,
                tx.external_wallet,
                tx.counterparty_id,
                getattr(tx.source_type, "value", tx.source_type),
                tx.notes,
            ])
        return buffer.getvalue()

    def to_tsv(self, transactions) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter="\t")
        writer.writerow(self.headers)
        for tx in transactions:
            writer.writerow([
                tx.id,
                tx.tx_datetime,
                getattr(tx.direction, "value", tx.direction),
                tx.amount,
                tx.token_symbol,
                tx.tx_hash,
                tx.external_wallet,
                tx.counterparty_id,
                getattr(tx.source_type, "value", tx.source_type),
                tx.notes,
            ])
        return buffer.getvalue()
