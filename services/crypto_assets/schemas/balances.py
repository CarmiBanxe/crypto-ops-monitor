from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer

from services.crypto_assets.models import WalletSourceType


class BalanceSnapshotCreate(BaseModel):
    wallet_id: int
    token_symbol: str
    observed_at: str
    amount: Decimal
    source_type: WalletSourceType


class BalanceSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    wallet_id: int
    token_symbol: str
    observed_at: str
    amount: Decimal
    source_type: WalletSourceType

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> str:
        return format(value, "f")
