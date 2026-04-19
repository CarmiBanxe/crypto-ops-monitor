from services.crypto_assets.db import engine
from services.crypto_assets.models import Base


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
