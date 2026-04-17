from sqlalchemy import select
from sqlalchemy.orm import Session
from services.crypto_assets.models import Wallet


class WalletRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, wallet: Wallet) -> Wallet:
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def get(self, wallet_id: int) -> Wallet | None:
        return self.db.get(Wallet, wallet_id)

    def list(self) -> list[Wallet]:
        return list(self.db.scalars(select(Wallet).order_by(Wallet.id)).all())

    def find_by_network_and_address(self, network_id: int, address: str) -> Wallet | None:
        stmt = select(Wallet).where(
            Wallet.network_id == network_id,
            Wallet.address == address,
        )
        return self.db.scalars(stmt).first()

    def update(self, wallet: Wallet) -> Wallet:
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet
