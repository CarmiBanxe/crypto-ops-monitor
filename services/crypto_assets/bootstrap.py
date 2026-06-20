from services.crypto_assets.db import engine
from services.crypto_assets.models import Base


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":  # pragma: no cover - operational migrate entrypoint
    init_db()
    print("DB bootstrap complete: all models registered, tables created.")
