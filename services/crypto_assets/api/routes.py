from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from services.crypto_assets.audit import record_audit
from services.crypto_assets.db import get_db
from services.crypto_assets.models import (
    Network,
    WalletSourceType,
)
from services.crypto_assets.repositories.ingestion_repository import IngestionRunRepository
from services.crypto_assets.repositories.transaction_repository import TransactionRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.schemas.ingestion import IngestionRunRead
from services.crypto_assets.schemas.transactions import TransactionRead
from services.crypto_assets.schemas.wallets import WalletCreate, WalletRead, WalletUpdate
from services.crypto_assets.security import CurrentUser, get_current_user
from services.crypto_assets.service.ingestion_service import IngestionService
from services.crypto_assets.service.transaction_service import TransactionService
from services.crypto_assets.service.wallet_service import WalletService

router = APIRouter(prefix="/crypto", tags=["crypto"])


def ensure_default_network(db: Session) -> Network:
    network = db.query(Network).filter_by(identifier="ethereum").first()
    if not network:
        network = Network(name="Ethereum", identifier="ethereum")
        db.add(network)
        db.commit()
        db.refresh(network)
    return network


@router.get("/wallets", response_model=list[WalletRead])
def list_wallets(
    network_id: int | None = Query(default=None),
    source_type: WalletSourceType | None = Query(default=None),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = WalletService(WalletRepository(db))
    wallets = service.list_wallets()
    if network_id is not None:
        wallets = [w for w in wallets if w.network_id == network_id]
    if source_type is not None:
        wallets = [w for w in wallets if w.source_type == source_type]
    return wallets


@router.post("/wallets", response_model=WalletRead)
def create_wallet(
    payload: WalletCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = WalletService(WalletRepository(db))
    wallet = service.create_wallet(payload)
    record_audit(
        actor=user.username,
        action="CREATE_WALLET",
        object_type="wallet",
        object_ref=str(wallet.id),
        after={"address": wallet.address, "network_id": wallet.network_id},
    )
    return wallet


@router.get("/wallets/{wallet_id}", response_model=WalletRead)
def get_wallet(
    wallet_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = WalletService(WalletRepository(db))
    wallet = service.get_wallet(wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@router.patch("/wallets/{wallet_id}", response_model=WalletRead)
def update_wallet(
    wallet_id: int,
    payload: WalletUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = WalletService(WalletRepository(db))
    existing = service.get_wallet(wallet_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    before = {
        "display_name": existing.display_name,
        "source_ref": existing.source_ref,
        "wallet_type": existing.wallet_type.value,
        "status": existing.status.value,
    }
    wallet = service.update_wallet(wallet_id, payload)
    record_audit(
        actor=user.username,
        action="UPDATE_WALLET",
        object_type="wallet",
        object_ref=str(wallet.id),
        before=before,
        after={
            "display_name": wallet.display_name,
            "source_ref": wallet.source_ref,
            "wallet_type": wallet.wallet_type.value,
            "status": wallet.status.value,
        },
    )
    return wallet


@router.post("/ingestion/ailink-sync", response_model=IngestionRunRead)
def run_ailink_sync(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    ensure_default_network(db)
    service = IngestionService(
        ingestion_repo=IngestionRunRepository(db),
        wallet_repo=WalletRepository(db),
    )
    run = service.run_ailink_wallet_sync()
    record_audit(
        actor=user.username,
        action="TRIGGER_AILINK_SYNC",
        object_type="ingestion_run",
        object_ref=str(run.id),
        after=run.stats_json,
    )
    return run


@router.get("/ingestion/runs", response_model=list[IngestionRunRead])
def list_ingestion_runs(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    repo = IngestionRunRepository(db)
    return repo.list()


@router.get("/ingestion/runs/{run_id}", response_model=IngestionRunRead)
def get_ingestion_run(
    run_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    repo = IngestionRunRepository(db)
    run = repo.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return run


@router.get("/transactions", response_model=list[TransactionRead])
def list_transactions(
    wallet_id: int | None = Query(default=None),
    source_type: WalletSourceType | None = Query(default=None),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = TransactionService(TransactionRepository(db))
    txs = service.list_transactions()
    if wallet_id is not None:
        txs = [t for t in txs if t.internal_wallet_id == wallet_id]
    if source_type is not None:
        txs = [t for t in txs if t.source_type == source_type]
    return txs


@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = TransactionService(TransactionRepository(db))
    tx = service.get_transaction(transaction_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx
