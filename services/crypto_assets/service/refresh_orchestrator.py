from datetime import UTC, datetime
from decimal import Decimal

from services.crypto_assets.models import IngestionRun, IngestionStatus, IngestionTriggerType, WalletSourceType
from services.crypto_assets.repositories.balance_repository import BalanceRepository
from services.crypto_assets.repositories.ingestion_repository import IngestionRunRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.service.balance_service import BalanceService
from services.crypto_assets.service.source_registry import SourceRegistry


class RefreshAllOrchestrator:
    def __init__(
        self,
        ingestion_repo: IngestionRunRepository,
        wallet_repo: WalletRepository,
        balance_repo: BalanceRepository,
        registry: SourceRegistry,
    ):
        self.ingestion_repo = ingestion_repo
        self.wallet_repo = wallet_repo
        self.balance_repo = balance_repo
        self.registry = registry

    @staticmethod
    def _wallet_network_code(wallet) -> str:
        network = getattr(wallet, "network", None)
        if network is not None:
            identifier = getattr(network, "identifier", None)
            if isinstance(identifier, str) and identifier:
                return identifier
            name = getattr(network, "name", None)
            if isinstance(name, str) and name:
                return name.lower()
        network_code = getattr(wallet, "network_code", None)
        if isinstance(network_code, str) and network_code:
            return network_code
        return "ethereum"

    def refresh_all(self, token_symbol: str = "USDC") -> IngestionRun:
        run = self.ingestion_repo.create(
            IngestionRun(
                connector_type="REFRESH_ALL",
                trigger_type=IngestionTriggerType.MANUAL,
                status=IngestionStatus.RUNNING,
                stats_json={"wallets_processed": 0, "snapshots_created": 0, "errors": 0},
            )
        )
        balance_service = BalanceService(self.balance_repo)
        processed = 0
        snapshots = 0
        errors = 0
        for wallet in self.wallet_repo.list():
            try:
                network_code = self._wallet_network_code(wallet)
                connector = self.registry.get_blockchain_connector(network_code)
                amount = connector.fetch_balance(wallet.address, token_symbol)
                if amount > Decimal("0"):
                    balance_service.record_snapshot(
                        wallet_id=wallet.id,
                        token_symbol=token_symbol,
                        amount=amount,
                        source_type=WalletSourceType.MANUAL,
                    )
                    snapshots += 1
                processed += 1
            except Exception:
                errors += 1
        run.status = IngestionStatus.SUCCEEDED
        run.stats_json = {
            "wallets_processed": processed,
            "snapshots_created": snapshots,
            "errors": errors,
            "finished_at": datetime.now(UTC).isoformat(),
        }
        return self.ingestion_repo.update(run)
