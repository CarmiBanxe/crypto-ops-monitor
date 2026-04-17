from services.crypto_assets.models.comments import TransactionComment
from services.crypto_assets.repositories.comment_repository import CommentRepository


class CommentService:
    def __init__(self, repo: CommentRepository):
        self.repo = repo

    def create_comment(self, transaction_id: int, author: str, body: str) -> TransactionComment:
        entity = TransactionComment(
            transaction_id=transaction_id,
            author=author,
            body=body,
        )
        return self.repo.create(entity)

    def list_comments(self, transaction_id: int):
        return self.repo.list_by_transaction(transaction_id)
