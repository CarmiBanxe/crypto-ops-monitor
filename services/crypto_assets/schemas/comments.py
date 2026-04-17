from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    body: str


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    transaction_id: int
    author: str
    body: str


class TagCreate(BaseModel):
    tag: str


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    transaction_id: int
    tag: str
    author: str
