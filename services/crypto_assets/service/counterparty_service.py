from services.crypto_assets.models import Counterparty, CounterpartyWalletLink
from services.crypto_assets.repositories.counterparty_repository import CounterpartyRepository
from services.crypto_assets.repositories.counterparty_wallet_link_repository import (
    CounterpartyWalletLinkRepository,
)
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.schemas.counterparties import (
    CounterpartyCreate,
    CounterpartyUpdate,
    CounterpartyWalletLinkCreate,
)


class CounterpartyService:
    def __init__(
        self,
        repo: CounterpartyRepository,
        link_repo: CounterpartyWalletLinkRepository,
        wallet_repo: WalletRepository,
    ):
        self.repo = repo
        self.link_repo = link_repo
        self.wallet_repo = wallet_repo

    def create_counterparty(self, data: CounterpartyCreate) -> Counterparty:
        entity = Counterparty(**data.model_dump())
        return self.repo.create(entity)

    def list_counterparties(self):
        return self.repo.list()

    def get_counterparty(self, counterparty_id: int):
        return self.repo.get(counterparty_id)

    def update_counterparty(self, counterparty_id: int, data: CounterpartyUpdate):
        entity = self.repo.get(counterparty_id)
        if entity is None:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)
        return self.repo.update(entity)

    def delete_counterparty(self, counterparty_id: int) -> bool:
        entity = self.repo.get(counterparty_id)
        if entity is None:
            return False

        links = self.link_repo.find_by_counterparty(counterparty_id)
        for link in links:
            self.link_repo.delete(link)

        self.repo.delete(entity)
        return True

    def link_wallet(self, data: CounterpartyWalletLinkCreate):
        counterparty = self.repo.get(data.counterparty_id)
        wallet = self.wallet_repo.get(data.wallet_id)
        if counterparty is None or wallet is None:
            return None
        existing = self.link_repo.find(data.counterparty_id, data.wallet_id)
        if existing:
            return existing
        entity = CounterpartyWalletLink(**data.model_dump())
        return self.link_repo.create(entity)

    def list_links(self):
        return self.link_repo.list_all()
