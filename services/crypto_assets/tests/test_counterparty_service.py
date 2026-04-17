import services.crypto_assets.db as db_mod
from services.crypto_assets.models import Network, WalletSourceType, WalletType
from services.crypto_assets.repositories.wallet_repository import WalletRepository
from services.crypto_assets.repositories.counterparty_repository import CounterpartyRepository
from services.crypto_assets.repositories.counterparty_wallet_link_repository import CounterpartyWalletLinkRepository
from services.crypto_assets.service.wallet_service import WalletService
from services.crypto_assets.service.counterparty_service import CounterpartyService
from services.crypto_assets.schemas.wallets import WalletCreate
from services.crypto_assets.schemas.counterparties import (
    CounterpartyCreate,
    CounterpartyUpdate,
    CounterpartyWalletLinkCreate,
)


def seed_ethereum(db):
    network = Network(name="Ethereum", identifier="ethereum")
    db.add(network)
    db.commit()
    db.refresh(network)
    return network


def test_counterparty_crud_and_linking():
    db = db_mod.SessionLocal()
    try:
        network = seed_ethereum(db)

        wallet_service = WalletService(WalletRepository(db))
        wallet = wallet_service.create_wallet(
            WalletCreate(
                address="0xcp001",
                display_name="Counterparty Link Wallet",
                network_id=network.id,
                source_type=WalletSourceType.MANUAL,
                source_ref="manual-cp-1",
                wallet_type=WalletType.NON_CUSTODY,
            )
        )

        service = CounterpartyService(
            repo=CounterpartyRepository(db),
            link_repo=CounterpartyWalletLinkRepository(db),
            wallet_repo=WalletRepository(db),
        )

        cp = service.create_counterparty(
            CounterpartyCreate(
                name="Stillman",
                risk_class="MEDIUM",
                properties_json={"source": "test"},
            )
        )
        assert cp.id is not None
        assert cp.name == "Stillman"

        updated = service.update_counterparty(
            cp.id,
            CounterpartyUpdate(risk_class="HIGH"),
        )
        assert updated is not None
        assert updated.risk_class == "HIGH"

        link = service.link_wallet(
            CounterpartyWalletLinkCreate(
                counterparty_id=cp.id,
                wallet_id=wallet.id,
            )
        )
        assert link is not None
        assert link.counterparty_id == cp.id
        assert link.wallet_id == wallet.id

        links = service.list_links()
        assert any(item.wallet_id == wallet.id for item in links)

        assert service.delete_counterparty(cp.id) is True

        assert service.get_counterparty(cp.id) is None
    finally:
        db.close()
