from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from services.crypto_assets.audit import log_audit_event
from services.crypto_assets.db import get_db
from services.crypto_assets.models import (
    Network,
    WalletSourceType,
)
from services.crypto_assets.models.folders import ApprovalRequest, WalletFolder, WalletFolderLink, WalletTag
from services.crypto_assets.repositories.approval_repository import ApprovalRepository
from services.crypto_assets.repositories.folder_repository import FolderRepository
from services.crypto_assets.repositories.ingestion_repository import IngestionRunRepository
from services.crypto_assets.repositories.transaction_repository import TransactionRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.schemas.folders import (
    ApprovalRequestRead,
    FolderCreate,
    FolderRead,
    WalletTagCreate,
    WalletTagRead,
)
from services.crypto_assets.schemas.ingestion import IngestionRunRead
from services.crypto_assets.schemas.transactions import TransactionRead
from services.crypto_assets.schemas.wallets import WalletCreate, WalletRead, WalletUpdate
from services.crypto_assets.security import CurrentUser, get_current_user
from services.crypto_assets.service.ingestion_service import IngestionService
from services.crypto_assets.service.rbac import require_write_access
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


# --- Wallets ---

@router.get("/wallets", response_model=list[WalletRead])
def list_wallets(
    network_id: int | None = Query(default=None),
    source_type: WalletSourceType | None = Query(default=None),
    display_name: str | None = Query(default=None),
    address: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = WalletService(WalletRepository(db))
    wallets = service.list_wallets()
    if network_id is not None:
        wallets = [w for w in wallets if w.network_id == network_id]
    if source_type is not None:
        wallets = [w for w in wallets if w.source_type == source_type]
    if display_name is not None:
        wallets = [w for w in wallets if w.display_name and display_name.lower() in w.display_name.lower()]
    if address is not None:
        wallets = [w for w in wallets if address.lower() in w.address.lower()]
    return wallets


@router.post("/wallets", response_model=WalletRead)
def create_wallet(
    payload: WalletCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    service = WalletService(WalletRepository(db))
    wallet = service.create_wallet(payload)
    log_audit_event(
        actor=user.username,
        action="CREATE_WALLET",
        details={"address": wallet.address, "network_id": wallet.network_id},
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
    require_write_access(user)
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
    log_audit_event(
        actor=user.username,
        action="UPDATE_WALLET",
        details={"before": before, "after": {
            "display_name": wallet.display_name,
            "source_ref": wallet.source_ref,
            "wallet_type": wallet.wallet_type.value,
            "status": wallet.status.value,
        }},
    )
    return wallet


# --- Ingestion ---

@router.post("/ingestion/ailink-sync", response_model=IngestionRunRead)
def run_ailink_sync(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    ensure_default_network(db)
    service = IngestionService(
        ingestion_repo=IngestionRunRepository(db),
        wallet_repo=WalletRepository(db),
    )
    run = service.run_ailink_wallet_sync()
    log_audit_event(
        actor=user.username,
        action="TRIGGER_AILINK_SYNC",
        details=run.stats_json,
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


# --- Transactions ---

@router.get("/transactions", response_model=list[TransactionRead])
def list_transactions(
    wallet_id: int | None = Query(default=None),
    source_type: WalletSourceType | None = Query(default=None),
    token_symbol: str | None = Query(default=None),
    direction: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = TransactionService(TransactionRepository(db))
    txs = service.list_transactions()
    if wallet_id is not None:
        txs = [t for t in txs if t.internal_wallet_id == wallet_id]
    if source_type is not None:
        txs = [t for t in txs if t.source_type == source_type]
    if token_symbol is not None:
        txs = [t for t in txs if t.token_symbol.upper() == token_symbol.upper()]
    if direction is not None:
        txs = [t for t in txs if t.direction.value == direction.upper()]
    if date_from is not None:
        txs = [t for t in txs if t.tx_datetime >= date_from]
    if date_to is not None:
        txs = [t for t in txs if t.tx_datetime <= date_to]
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



# --- Folders / Wallet Tags / Approvals ---

@router.get("/folders", response_model=list[FolderRead])
def list_folders(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    repo = FolderRepository(db)
    return repo.list_folders()


@router.post("/folders", response_model=FolderRead)
def create_folder(
    payload: FolderCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    repo = FolderRepository(db)
    folder = repo.create_folder(WalletFolder(
        name=payload.name,
        parent_id=payload.parent_id,
        created_by=user.username,
    ))
    log_audit_event(
        actor=user.username,
        action="CREATE_WALLET_FOLDER",
        details={"folder_id": folder.id, "name": folder.name, "parent_id": folder.parent_id},
    )
    return folder


@router.post("/folders/{folder_id}/wallets/{wallet_id}", status_code=201)
def add_wallet_to_folder(
    folder_id: int,
    wallet_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    wallet_repo = WalletRepository(db)
    if wallet_repo.get(wallet_id) is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    repo = FolderRepository(db)
    folder_ids = {f.id for f in repo.list_folders()}
    if folder_id not in folder_ids:
        raise HTTPException(status_code=404, detail="Folder not found")
    link = repo.add_wallet_to_folder(WalletFolderLink(folder_id=folder_id, wallet_id=wallet_id))
    log_audit_event(
        actor=user.username,
        action="ADD_WALLET_TO_FOLDER",
        details={"folder_id": folder_id, "wallet_id": wallet_id, "link_id": link.id},
    )
    return {"id": link.id, "folder_id": folder_id, "wallet_id": wallet_id}


@router.get("/wallets/{wallet_id}/tags", response_model=list[WalletTagRead])
def list_wallet_tags(
    wallet_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    wallet_repo = WalletRepository(db)
    if wallet_repo.get(wallet_id) is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    repo = FolderRepository(db)
    return repo.list_tags_for_wallet(wallet_id)


@router.post("/wallets/{wallet_id}/tags", response_model=WalletTagRead)
def create_wallet_tag(
    wallet_id: int,
    payload: WalletTagCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    wallet_repo = WalletRepository(db)
    if wallet_repo.get(wallet_id) is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    repo = FolderRepository(db)
    tag = repo.create_wallet_tag(WalletTag(
        wallet_id=wallet_id,
        tag=payload.tag,
        author=user.username,
    ))
    log_audit_event(
        actor=user.username,
        action="CREATE_WALLET_TAG",
        details={"wallet_id": wallet_id, "tag": tag.tag},
    )
    return tag


@router.get("/approvals", response_model=list[ApprovalRequestRead])
def list_approvals(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    repo = ApprovalRepository(db)
    return repo.list_pending()


@router.post("/approvals", response_model=ApprovalRequestRead)
def create_approval(
    payload: dict,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    repo = ApprovalRepository(db)
    req = repo.create(ApprovalRequest(
        action_type=payload["action_type"],
        object_type=payload["object_type"],
        object_ref=str(payload["object_ref"]),
        payload_json=payload.get("payload_json"),
        status="PENDING",
        initiator=user.username,
    ))
    log_audit_event(
        actor=user.username,
        action="CREATE_APPROVAL_REQUEST",
        details={"approval_id": req.id, "action_type": req.action_type, "object_type": req.object_type},
    )
    return req


@router.patch("/approvals/{approval_id}", response_model=ApprovalRequestRead)
def update_approval(
    approval_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    repo = ApprovalRepository(db)
    req = repo.get(approval_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Approval request not found")
    status_value = payload.get("status")
    if status_value not in {"APPROVED", "REJECTED"}:
        raise HTTPException(status_code=422, detail="status must be APPROVED or REJECTED")
    req.status = status_value
    req.approver = user.username
    updated = repo.update(req)
    log_audit_event(
        actor=user.username,
        action="UPDATE_APPROVAL_REQUEST",
        details={"approval_id": updated.id, "status": updated.status, "approver": updated.approver},
    )
    return updated

# --- Transaction Comments/Tags ---

