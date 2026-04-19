from services.crypto_assets.models import (
    IngestionRun,
    IngestionStatus,
    IngestionTriggerType,
    RecordStatus,
    Wallet,
    WalletSourceType,
    WalletType,
)
from services.crypto_assets.repositories.ingestion_repository import IngestionRunRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository


class MockAilinkWalletSyncAdapter:
    def fetch_wallets(self) -> list[dict]:
        return [
            {
                "address": "0xabc123",
                "display_name": "Ailink Main Wallet",
                "network_id": 1,
                "source_ref": "ailink-wallet-001",
                "wallet_type": "CUSTODY",
            },
            {
                "address": "0xdef456",
                "display_name": "Ailink Reserve Wallet",
                "network_id": 1,
                "source_ref": "ailink-wallet-002",
                "wallet_type": "CUSTODY",
            },
        ]


class IngestionService:
    def __init__(
        self,
        ingestion_repo: IngestionRunRepository,
        wallet_repo: WalletRepository,
        adapter: MockAilinkWalletSyncAdapter | None = None,
    ):
        self.ingestion_repo = ingestion_repo
        self.wallet_repo = wallet_repo
        self.adapter = adapter or MockAilinkWalletSyncAdapter()

    def run_ailink_wallet_sync(self) -> IngestionRun:
        run = IngestionRun(
            connector_type="AILINK_WALLET_SYNC",
            trigger_type=IngestionTriggerType.MANUAL,
            status=IngestionStatus.RUNNING,
            stats_json={"created": 0, "updated": 0},
        )
        run = self.ingestion_repo.create(run)

        created = 0
        updated = 0

        for item in self.adapter.fetch_wallets():
            existing = self.wallet_repo.find_by_network_and_address(
                network_id=item["network_id"],
                address=item["address"],
            )
            if existing:
                existing.display_name = item["display_name"]
                existing.source_ref = item["source_ref"]
                existing.wallet_type = WalletType(item["wallet_type"])
                existing.status = RecordStatus.ACTIVE
                self.wallet_repo.update(existing)
                updated += 1
            else:
                wallet = Wallet(
                    address=item["address"],
                    display_name=item["display_name"],
                    network_id=item["network_id"],
                    source_type=WalletSourceType.AILINK,
                    source_ref=item["source_ref"],
                    wallet_type=WalletType(item["wallet_type"]),
                    status=RecordStatus.ACTIVE,
                )
                self.wallet_repo.create(wallet)
                created += 1

        run.status = IngestionStatus.SUCCEEDED
        run.stats_json = {"created": created, "updated": updated}
        return self.ingestion_repo.update(run)
