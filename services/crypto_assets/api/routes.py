from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from services.crypto_assets.audit import log_audit_event
from services.crypto_assets.db import get_db
from services.crypto_assets.models import Network
from services.crypto_assets.repositories.counterparty_repository import CounterpartyRepository
from services.crypto_assets.repositories.counterparty_wallet_link_repository import (
    CounterpartyWalletLinkRepository,
)
from services.crypto_assets.repositories.ingestion_repository import IngestionRunRepository
from services.crypto_assets.repositories.transaction_repository import TransactionRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.schemas.counterparties import (
    CounterpartyCreate,
    CounterpartyRead,
    CounterpartyUpdate,
    CounterpartyWalletLinkCreate,
    CounterpartyWalletLinkRead,
)
from services.crypto_assets.schemas.ingestion import IngestionRunRead
from services.crypto_assets.schemas.transactions import TransactionRead
from services.crypto_assets.schemas.wallets import WalletCreate, WalletRead
from services.crypto_assets.security import CurrentUser, get_current_user
from services.crypto_assets.service.counterparty_service import CounterpartyService
from services.crypto_assets.service.ingestion_service import IngestionService
from services.crypto_assets.service.transaction_service import TransactionService
from services.crypto_assets.service.wallet_service import WalletService

router = APIRouter(prefix="/crypto", tags=["crypto-assets"])


def require_write_role(user: CurrentUser) -> None:
    if user.role not in {"FINANCE_DIRECTOR", "HEAD_OF_PAYMENTS"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


def ensure_default_network(db: Session) -> None:
    network = db.query(Network).filter_by(identifier="ethereum").first()
    if not network:
        network = Network(name="Ethereum", identifier="ethereum")
        db.add(network)
        db.commit()


@router.get("/wallets", response_model=list[WalletRead])
def list_wallets(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = WalletService(WalletRepository(db))
    return service.list_wallets()


@router.post("/wallets", response_model=WalletRead)
def create_wallet(
    payload: WalletCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_role(user)
    ensure_default_network(db)
    service = WalletService(WalletRepository(db))
    wallet = service.create_wallet(payload)
    log_audit_event(user.username, "CREATE_WALLET", {"wallet_id": wallet.id, "address": wallet.address})
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


@router.post("/ingestion/ailink-sync", response_model=IngestionRunRead)
def run_ailink_sync(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_role(user)
    ensure_default_network(db)
    service = IngestionService(
        ingestion_repo=IngestionRunRepository(db),
        wallet_repo=WalletRepository(db),
    )
    run = service.run_ailink_wallet_sync()
    log_audit_event(user.username, "RUN_AILINK_SYNC", {"run_id": run.id, "status": run.status.value})
    return run


@router.get("/ingestion/runs", response_model=list[IngestionRunRead])
def list_ingestion_runs(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    repo = IngestionRunRepository(db)
    return repo.list()


@router.get("/transactions", response_model=list[TransactionRead])
def list_transactions(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = TransactionService(TransactionRepository(db))
    return service.list_transactions()


@router.get("/counterparties", response_model=list[CounterpartyRead])
def list_counterparties(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    return service.list_counterparties()


@router.post("/counterparties", response_model=CounterpartyRead)
def create_counterparty(
    payload: CounterpartyCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_role(user)
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    counterparty = service.create_counterparty(payload)
    log_audit_event(
        user.username,
        "CREATE_COUNTERPARTY",
        {"counterparty_id": counterparty.id, "name": counterparty.name},
    )
    return counterparty


@router.get("/counterparties/{counterparty_id}", response_model=CounterpartyRead)
def get_counterparty(
    counterparty_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    counterparty = service.get_counterparty(counterparty_id)
    if counterparty is None:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    return counterparty


@router.put("/counterparties/{counterparty_id}", response_model=CounterpartyRead)
def update_counterparty(
    counterparty_id: int,
    payload: CounterpartyUpdate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_role(user)
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    counterparty = service.update_counterparty(counterparty_id, payload)
    if counterparty is None:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    log_audit_event(
        user.username,
        "UPDATE_COUNTERPARTY",
        {"counterparty_id": counterparty.id},
    )
    return counterparty


@router.delete("/counterparties/{counterparty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_counterparty(
    counterparty_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_role(user)
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    deleted = service.delete_counterparty(counterparty_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    log_audit_event(user.username, "DELETE_COUNTERPARTY", {"counterparty_id": counterparty_id})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/counterparty-wallet-links", response_model=list[CounterpartyWalletLinkRead])
def list_counterparty_wallet_links(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    return service.list_links()


@router.post("/counterparty-wallet-links", response_model=CounterpartyWalletLinkRead)
def create_counterparty_wallet_link(
    payload: CounterpartyWalletLinkCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_role(user)
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    link = service.link_wallet(payload)
    if link is None:
        raise HTTPException(status_code=404, detail="Counterparty or wallet not found")
    log_audit_event(
        user.username,
        "LINK_COUNTERPARTY_WALLET",
        {"counterparty_id": link.counterparty_id, "wallet_id": link.wallet_id},
    )
    return link
