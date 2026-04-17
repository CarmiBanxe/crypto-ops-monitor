from pydantic import BaseModel, ConfigDict
from services.crypto_assets.models import CounterpartyKind, RecordStatus


class CounterpartyCreate(BaseModel):
    name: str
    kind: CounterpartyKind = CounterpartyKind.UNKNOWN
    risk_class: str | None = None
    properties_json: dict | None = None
    status: RecordStatus = RecordStatus.ACTIVE


class CounterpartyUpdate(BaseModel):
    name: str | None = None
    kind: CounterpartyKind | None = None
    risk_class: str | None = None
    properties_json: dict | None = None
    status: RecordStatus | None = None


class CounterpartyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    kind: CounterpartyKind
    risk_class: str | None
    properties_json: dict | None
    status: RecordStatus


class CounterpartyWalletLinkCreate(BaseModel):
    counterparty_id: int
    wallet_id: int


class CounterpartyWalletLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    counterparty_id: int
    wallet_id: int
