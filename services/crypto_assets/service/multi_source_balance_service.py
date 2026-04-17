from decimal import Decimal

from services.crypto_assets.models import WalletSourceType
from services.crypto_assets.service.balance_service import BalanceService
from services.crypto_assets.service.source_registry import SourceRegistry


class MultiSourceBalanceService:
    def __init__(self, balance_service: BalanceService, registry: SourceRegistry):
        self.balance_service = balance_service
        self.registry = registry

    def ingest_blockchain_balance(
        self,
        wallet_id: int,
        network_code: str,
        address: str,
        token_symbol: str,
    ):
        connector = self.registry.get_blockchain_connector(network_code)
        amount = connector.fetch_balance(address, token_symbol)
        return self.balance_service.record_snapshot(
            wallet_id=wallet_id,
            token_symbol=token_symbol,
            amount=amount,
            source_type=WalletSourceType.MANUAL,
        )

    def ingest_account_balance(
        self,
        wallet_id: int,
        source_code: str,
        account_id: str,
        token_symbol: str,
    ):
        adapter = self.registry.get_account_adapter(source_code)
        balances = adapter.fetch_account_balances(account_id)
        amount = balances.get(token_symbol, Decimal("0"))
        return self.balance_service.record_snapshot(
            wallet_id=wallet_id,
            token_symbol=token_symbol,
            amount=amount,
            source_type=WalletSourceType.MANUAL,
        )
