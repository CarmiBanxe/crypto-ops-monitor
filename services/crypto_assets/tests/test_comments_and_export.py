from decimal import Decimal

import services.crypto_assets.db as db_mod
from services.crypto_assets.models import (
    CanonicalTransaction,
    Direction,
    Network,
    WalletSourceType,
)
from services.crypto_assets.models.comments import TransactionComment, TransactionTag
from services.crypto_assets.repositories.comment_repository import CommentRepository
from services.crypto_assets.service.export_service import ExportService


def seed_tx(db):
    network = db.query(Network).filter_by(identifier="ethereum").first()
    if network is None:
        network = Network(name="Ethereum", identifier="ethereum")
        db.add(network)
        db.commit()
        db.refresh(network)
    tx = CanonicalTransaction(
        tx_datetime="2026-04-17T10:00:00Z",
        direction=Direction.IN,
        amount=Decimal("1.500000000000000000"),
        token_symbol="USDC",
        tx_hash="0xabc123hash",
        source_type=WalletSourceType.MANUAL,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def test_add_comment_and_tag():
    db = db_mod.SessionLocal()
    try:
        tx = seed_tx(db)
        repo = CommentRepository(db)

        comment = repo.create_comment(TransactionComment(
            transaction_id=tx.id,
            author="sasha",
            body="Checked — looks correct",
        ))
        assert comment.id is not None
        assert comment.author == "sasha"

        tag = repo.create_tag(TransactionTag(
            transaction_id=tx.id,
            tag="INVESTIGATED",
            author="anton",
        ))
        assert tag.id is not None
        assert tag.tag == "INVESTIGATED"

        comments = repo.list_by_transaction(tx.id)
        assert len(comments) == 1

        tags = repo.list_tags_by_transaction(tx.id)
        assert len(tags) == 1
    finally:
        db.close()


def test_export_csv():
    db = db_mod.SessionLocal()
    try:
        tx = seed_tx(db)
        csv_output = ExportService.transactions_to_csv([tx])
        lines = csv_output.strip().split("\n")
        assert len(lines) == 2
        assert "USDC" in lines[1]
        assert "1.500000000000000000" in lines[1]
    finally:
        db.close()


def test_export_tsv():
    db = db_mod.SessionLocal()
    try:
        tx = seed_tx(db)
        tsv_output = ExportService.transactions_to_tsv([tx])
        lines = tsv_output.strip().split("\n")
        assert len(lines) == 2
        assert "\t" in lines[1]
    finally:
        db.close()
