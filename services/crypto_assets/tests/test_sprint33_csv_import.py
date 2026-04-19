import services.crypto_assets.db as db_mod
from services.crypto_assets.repositories.transaction_repository import TransactionRepository
from services.crypto_assets.service.csv_import_service import CSVImportError, CSVImportService


def test_csv_import_success():
    db = db_mod.SessionLocal()
    try:
        repo = TransactionRepository(db)
        service = CSVImportService(repo)
        content = (
            "tx_datetime,direction,amount,token_symbol,tx_hash,external_wallet,notes\n"
            "2026-04-17T10:00:00Z,IN,100.50,USDC,0xcsv-1,0xext-1,csv test\n"
            "2026-04-17T11:00:00Z,OUT,50.25,USDC,0xcsv-2,0xext-2,\n"
        )
        result = service.import_csv(content)
        assert result["imported"] == 2
        assert result["errors"] == []
        assert len(result["file_fingerprint"]) == 64
    finally:
        db.close()


def test_csv_import_missing_columns_raises():
    db = db_mod.SessionLocal()
    try:
        repo = TransactionRepository(db)
        service = CSVImportService(repo)
        bad = "tx_datetime,amount\n2026-04-17,100\n"
        try:
            service.import_csv(bad)
            raise AssertionError("should have raised")
        except CSVImportError as e:
            assert "Missing required columns" in str(e)
    finally:
        db.close()


def test_csv_import_fingerprint_deterministic():
    content = "a,b,c\n1,2,3\n"
    fp1 = CSVImportService.file_fingerprint(content)
    fp2 = CSVImportService.file_fingerprint(content)
    assert fp1 == fp2
    assert len(fp1) == 64


def test_csv_import_row_fingerprint():
    row = {"tx_hash": "0xh", "tx_datetime": "2026-04-17", "token_symbol": "USDC", "amount": "100"}
    fp = CSVImportService.row_fingerprint(row)
    assert len(fp) == 64


def test_csv_import_empty_header_raises():
    db = db_mod.SessionLocal()
    try:
        repo = TransactionRepository(db)
        service = CSVImportService(repo)
        try:
            service.import_csv("")
            raise AssertionError("should have raised")
        except CSVImportError:
            pass
    finally:
        db.close()
