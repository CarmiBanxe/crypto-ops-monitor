from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from services.crypto_assets.audit import log_audit_event
from services.crypto_assets.connectors.mock_ethereum import MockEthereumConnector
from services.crypto_assets.db import get_db
from services.crypto_assets.repositories.balance_repository import BalanceRepository
from services.crypto_assets.repositories.ingestion_repository import IngestionRunRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.security import CurrentUser, get_current_user
from services.crypto_assets.service.rbac import require_write_access
from services.crypto_assets.service.reconciliation_service import ReconciliationService
from services.crypto_assets.service.refresh_orchestrator import RefreshAllOrchestrator
from services.crypto_assets.service.source_registry import SourceRegistry

router = APIRouter(prefix="/crypto", tags=["operational"])


def _default_registry() -> SourceRegistry:
    registry = SourceRegistry()
    registry.register_blockchain_connector("ethereum", MockEthereumConnector())
    return registry


@router.post("/ingestion/refresh-all")
def refresh_all_transactions(
    token_symbol: str = Query(default="USDC"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    require_write_access(user)
    orchestrator = RefreshAllOrchestrator(
        ingestion_repo=IngestionRunRepository(db),
        wallet_repo=WalletRepository(db),
        balance_repo=BalanceRepository(db),
        registry=_default_registry(),
    )
    run = orchestrator.refresh_all(token_symbol=token_symbol)
    log_audit_event(
        actor=user.username,
        action="REFRESH_ALL_TRIGGERED",
        details=run.stats_json,
    )
    return {
        "run_id": run.id,
        "status": run.status.value,
        "stats": run.stats_json,
    }


@router.get("/reconciliation/coverage")
def reconciliation_coverage(
    token_symbol: str = Query(default="USDC"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = ReconciliationService(BalanceRepository(db), WalletRepository(db))
    return service.scan_all_wallets(token_symbol)


@router.get("/reconciliation/wallet/{wallet_id}")
def reconcile_wallet(
    wallet_id: int,
    token_symbol: str = Query(...),
    expected: str = Query(...),
    tolerance: str = Query(default="0.01"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    service = ReconciliationService(BalanceRepository(db), WalletRepository(db))
    return service.check_wallet(
        wallet_id=wallet_id,
        token_symbol=token_symbol,
        expected=Decimal(expected),
        tolerance=Decimal(tolerance),
    )
