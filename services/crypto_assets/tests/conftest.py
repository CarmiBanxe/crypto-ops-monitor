import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from services.crypto_assets.models import Base
from services.crypto_assets.db import get_db
from api.main import app


@pytest.fixture(autouse=True)
def test_db():
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    import services.crypto_assets.db as db_mod
    original_session = db_mod.SessionLocal
    db_mod.SessionLocal = TestSession

    yield engine

    app.dependency_overrides.clear()
    db_mod.SessionLocal = original_session
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
