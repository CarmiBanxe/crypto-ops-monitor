from services.crypto_assets.models import Base

EXPECTED_TABLES = {
    "crypto_networks",
    "crypto_wallets",
    "crypto_counterparties",
    "crypto_counterparty_wallet_links",
    "crypto_source_accounts",
    "crypto_ingestion_runs",
    "crypto_raw_transaction_events",
    "crypto_canonical_transactions",
    "crypto_wallet_balance_snapshots",
}


def test_expected_tables_registered():
    assert EXPECTED_TABLES.issubset(set(Base.metadata.tables.keys()))
