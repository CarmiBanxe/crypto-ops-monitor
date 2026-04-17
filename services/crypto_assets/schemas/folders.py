from pydantic import BaseModel, ConfigDict


class FolderCreate(BaseModel):
    name: str
    parent_id: int | None = None


class FolderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    parent_id: int | None
    created_by: str


class WalletTagCreate(BaseModel):
    tag: str


class WalletTagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    wallet_id: int
    tag: str
    author: str


class ApprovalRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    action_type: str
    object_type: str
    object_ref: str
    payload_json: str | None
    status: str
    initiator: str
    approver: str | None
