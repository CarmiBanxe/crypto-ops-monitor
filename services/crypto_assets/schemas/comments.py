from pydantic import BaseModel, ConfigDict


class TransactionCommentCreate(BaseModel):
    transaction_id: int
    body: str


class TransactionCommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: int
    author: str
    body: str
