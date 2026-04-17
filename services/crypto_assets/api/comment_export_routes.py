from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from services.crypto_assets.audit import log_audit_event
from services.crypto_assets.db import get_db
from services.crypto_assets.repositories.comment_repository import CommentRepository
from services.crypto_assets.repositories.transaction_repository import TransactionRepository
from services.crypto_assets.schemas.comments import (
    TransactionCommentCreate,
    TransactionCommentRead,
)
from services.crypto_assets.security import CurrentUser, get_current_user
from services.crypto_assets.service.comment_service import CommentService
from services.crypto_assets.service.export_service import ExportService
from services.crypto_assets.service.rbac import require_write_access
from services.crypto_assets.service.transaction_service import TransactionService

router = APIRouter(prefix="/crypto", tags=["crypto-comments-export"])


@router.get("/transactions/export")
def export_transactions(
    format: str = Query(default="csv"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    tx_service = TransactionService(TransactionRepository(db))
    export_service = ExportService()
    transactions = tx_service.list_transactions()

    if format == "tsv":
        content = export_service.to_tsv(transactions)
        media_type = "text/tab-separated-values; charset=utf-8"
    else:
        content = export_service.to_csv(transactions)
        media_type = "text/csv; charset=utf-8"

    return PlainTextResponse(content=content, media_type=media_type)


@router.get("/transactions/{transaction_id}/comments", response_model=list[TransactionCommentRead])
def list_transaction_comments(
    transaction_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = CommentService(CommentRepository(db))
    return service.list_comments(transaction_id)


@router.post("/transactions/{transaction_id}/comments", response_model=TransactionCommentRead)
def create_transaction_comment(
    transaction_id: int,
    payload: TransactionCommentCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    service = CommentService(CommentRepository(db))
    comment = service.create_comment(
        transaction_id=transaction_id,
        author=user.username,
        body=payload.body,
    )
    log_audit_event(
        actor=user.username,
        action="CREATE_TRANSACTION_COMMENT",
        details={"transaction_id": transaction_id, "comment_id": comment.id},
    )
    return comment
