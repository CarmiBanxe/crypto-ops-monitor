from sqlalchemy import select
from sqlalchemy.orm import Session

from services.crypto_assets.models.folders import WalletFolder, WalletFolderLink, WalletTag


class FolderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_folder(self, folder: WalletFolder) -> WalletFolder:
        self.db.add(folder)
        self.db.commit()
        self.db.refresh(folder)
        return folder

    def list_folders(self) -> list[WalletFolder]:
        return list(self.db.scalars(select(WalletFolder).order_by(WalletFolder.id)).all())

    def add_wallet_to_folder(self, link: WalletFolderLink) -> WalletFolderLink:
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def list_wallets_in_folder(self, folder_id: int) -> list[int]:
        stmt = select(WalletFolderLink.wallet_id).where(
            WalletFolderLink.folder_id == folder_id
        )
        return list(self.db.scalars(stmt).all())

    def create_wallet_tag(self, tag: WalletTag) -> WalletTag:
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def list_tags_for_wallet(self, wallet_id: int) -> list[WalletTag]:
        stmt = select(WalletTag).where(WalletTag.wallet_id == wallet_id).order_by(WalletTag.id)
        return list(self.db.scalars(stmt).all())
