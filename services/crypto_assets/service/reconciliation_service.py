from decimal import Decimal
from services.crypto_assets.repositories.balance_repository import BalanceRepository
from services.crypto_assets.repositories.wallet_repository import WalletRepository


class ReconciliationService:
    def __init__(self, balance_repo: BalanceRepository, wallet_repo: WalletRepository):
        self.balance_repo = balance_repo
        self.wallet_repo = wallet_repo

    def check_wallet(self, wallet_id: int, token_symbol: str, expected: Decimal,
                     tolerance: Decimal = Decimal("0.01")) -> dict:
        snapshot = self.balance_repo.latest_for_wallet(wallet_id, token_symbol)
        if snapshot is None:
            return {"wallet_id": wallet_id, "status": "NO_DATA", "expected": str(expected), "actual": None}
        diff = abs(snapshot.amount - expected)
        status = "OK" if diff <= tolerance else "MISMATCH"
        return {
            "wallet_id": wallet_id,
            "token_symbol": token_symbol,
            "status": status,
            "expected": str(expected),
            "actual": str(snapshot.amount),
            "diff": str(diff),
            "tolerance": str(tolerance),
        }

    def scan_all_wallets(self, token_symbol: str) -> dict:
        wallets = self.wallet_repo.list()
        with_data = 0
        without_data = 0
        for w in wallets:
            snap = self.balance_repo.latest_for_wallet(w.id, token_symbol)
            if snap:
                with_data += 1
            else:
                without_data += 1
        return {
            "total_wallets": len(wallets),
            "wallets_with_balance": with_data,
            "wallets_without_balance": without_data,
            "coverage_pct": round(100 * with_data / len(wallets), 2) if wallets else 0,
        }
