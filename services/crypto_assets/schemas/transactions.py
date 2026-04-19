from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer

from services.crypto_assets.models import Direction, WalletSourceType


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tx_datetime: str
    direction: Direction
    amount: Decimal
    token_symbol: str
    tx_hash: str
    internal_wallet_id: int | None
    external_wallet: str | None
    counterparty_id: int | None
    source_type: WalletSourceType
    notes: str | None

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> str:
        return format(value, "f")
