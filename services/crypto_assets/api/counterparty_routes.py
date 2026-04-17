from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from services.crypto_assets.audit import log_audit_event
from services.crypto_assets.db import get_db
from services.crypto_assets.repositories.counterparty_repository import CounterpartyRepository
from services.crypto_assets.repositories.counterparty_wallet_link_repository import CounterpartyWalletLinkRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.schemas.counterparties import (
    CounterpartyCreate,
    CounterpartyRead,
    CounterpartyUpdate,
    CounterpartyWalletLinkCreate,
    CounterpartyWalletLinkRead,
)
from services.crypto_assets.security import CurrentUser, get_current_user
from services.crypto_assets.service.counterparty_service import CounterpartyService
from services.crypto_assets.service.rbac import require_write_access

router = APIRouter(prefix="/crypto", tags=["crypto-counterparties"])


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
    require_write_access(user)
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    counterparty = service.create_counterparty(payload)
    log_audit_event(
        actor=user.username,
        action="CREATE_COUNTERPARTY",
        details={"counterparty_id": counterparty.id, "name": counterparty.name},
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
    require_write_access(user)
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    counterparty = service.update_counterparty(counterparty_id, payload)
    if counterparty is None:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    log_audit_event(
        actor=user.username,
        action="UPDATE_COUNTERPARTY",
        details={"counterparty_id": counterparty.id},
    )
    return counterparty


@router.delete("/counterparties/{counterparty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_counterparty(
    counterparty_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    deleted = service.delete_counterparty(counterparty_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Counterparty not found")
    log_audit_event(
        actor=user.username,
        action="DELETE_COUNTERPARTY",
        details={"counterparty_id": counterparty_id},
    )
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
    require_write_access(user)
    service = CounterpartyService(
        repo=CounterpartyRepository(db),
        link_repo=CounterpartyWalletLinkRepository(db),
        wallet_repo=WalletRepository(db),
    )
    link = service.link_wallet(payload)
    if link is None:
        raise HTTPException(status_code=404, detail="Counterparty or wallet not found")
    log_audit_event(
        actor=user.username,
        action="LINK_COUNTERPARTY_WALLET",
        details={"counterparty_id": link.counterparty_id, "wallet_id": link.wallet_id},
    )
    return link
