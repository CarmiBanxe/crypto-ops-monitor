from pydantic import BaseModel, ConfigDict

from services.crypto_assets.models import RecordStatus, WalletSourceType, WalletType


class WalletCreate(BaseModel):
    address: str
    display_name: str | None = None
    network_id: int
    source_type: WalletSourceType
    source_ref: str | None = None
    wallet_type: WalletType = WalletType.UNKNOWN
    status: RecordStatus = RecordStatus.ACTIVE


class WalletUpdate(BaseModel):
    display_name: str | None = None
    source_ref: str | None = None
    wallet_type: WalletType | None = None
    status: RecordStatus | None = None


class WalletRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address: str
    display_name: str | None
    network_id: int
    source_type: WalletSourceType
    source_ref: str | None
    wallet_type: WalletType
    status: RecordStatus
