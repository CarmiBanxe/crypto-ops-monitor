from services.crypto_assets.models import Wallet
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.schemas.wallets import WalletCreate, WalletUpdate


class WalletService:
    def __init__(self, repo: WalletRepository):
        self.repo = repo

    def create_wallet(self, data: WalletCreate) -> Wallet:
        wallet = Wallet(**data.model_dump())
        return self.repo.create(wallet)

    def get_wallet(self, wallet_id: int):
        return self.repo.get(wallet_id)

    def list_wallets(self):
        return self.repo.list()

    def update_wallet(self, wallet_id: int, data: WalletUpdate):
        wallet = self.repo.get(wallet_id)
        if wallet is None:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(wallet, key, value)
        return self.repo.update(wallet)
