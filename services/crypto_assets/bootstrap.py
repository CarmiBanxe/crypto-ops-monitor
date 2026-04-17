from services.crypto_assets.models import Base
from services.crypto_assets.db import engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
