from services.crypto_assets.repositories.transaction_repository import TransactionRepository


class TransactionService:
    def __init__(self, repo: TransactionRepository):
        self.repo = repo

    def list_transactions(self):
        return self.repo.list()

    def get_transaction(self, tx_id: int):
        return self.repo.get(tx_id)
