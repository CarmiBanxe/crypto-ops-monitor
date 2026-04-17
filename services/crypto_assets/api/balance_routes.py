from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.crypto_assets.audit import log_audit_event
from services.crypto_assets.db import get_db
from services.crypto_assets.models import WalletSourceType
from services.crypto_assets.repositories.balance_repository import BalanceRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.schemas.balances import BalanceSnapshotCreate, BalanceSnapshotRead
from services.crypto_assets.security import CurrentUser, get_current_user
from services.crypto_assets.service.balance_service import BalanceService
from services.crypto_assets.service.rbac import require_write_access
from services.crypto_assets.connectors.mock_ethereum import MockEthereumConnector

router = APIRouter(prefix="/crypto", tags=["balances"])


@router.get("/wallets/{wallet_id}/balances", response_model=list[BalanceSnapshotRead])
def list_wallet_balances(
    wallet_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = BalanceService(BalanceRepository(db))
    return service.list_wallet_balances(wallet_id)


@router.post("/wallets/{wallet_id}/balances", response_model=BalanceSnapshotRead)
def record_balance_snapshot(
    wallet_id: int,
    payload: BalanceSnapshotCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    if payload.wallet_id != wallet_id:
        raise HTTPException(status_code=400, detail="wallet_id mismatch")
    service = BalanceService(BalanceRepository(db))
    snapshot = service.record_snapshot(
        wallet_id=payload.wallet_id,
        token_symbol=payload.token_symbol,
        amount=payload.amount,
        source_type=payload.source_type,
        observed_at=payload.observed_at,
    )
    log_audit_event(
        actor=user.username,
        action="RECORD_BALANCE_SNAPSHOT",
        details={"wallet_id": wallet_id, "token": payload.token_symbol, "amount": str(payload.amount)},
    )
    return snapshot


@router.post("/ingestion/blockchain-balances/{wallet_id}")
def ingest_blockchain_balance(
    wallet_id: int,
    token_symbol: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    wallet_repo = WalletRepository(db)
    wallet = wallet_repo.get(wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    # Mock connector with demo balance
    connector = MockEthereumConnector(balances={
        wallet.address: {token_symbol: Decimal("1.0")},
    })
    amount = connector.fetch_balance(wallet.address, token_symbol)
    service = BalanceService(BalanceRepository(db))
    snapshot = service.record_snapshot(
        wallet_id=wallet_id,
        token_symbol=token_symbol,
        amount=amount,
        source_type=WalletSourceType.MANUAL,
    )
    log_audit_event(
        actor=user.username,
        action="INGEST_BLOCKCHAIN_BALANCE",
        details={"wallet_id": wallet_id, "token": token_symbol, "amount": str(amount)},
    )
    return {"snapshot_id": snapshot.id, "wallet_id": wallet_id, "token_symbol": token_symbol, "amount": str(amount)}
