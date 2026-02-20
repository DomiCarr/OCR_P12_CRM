# tests/conftest.py
"""
Pytest configuration and global fixtures.
Provides database engine and session management for tests.
Initializes Sentry for error tracking during tests.
"""

import os
from dotenv import load_dotenv
import pytest
import sentry_sdk
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config.config import Config
from app.models import Base
from app.utils.token_storage import TOKEN_FILE

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def init_sentry():
    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        environment="testing",
        traces_sample_rate=1.0
    )


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(Config.get_db_url())
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Provide a fully clean database for each test.
    Hard reset using TRUNCATE and AUTO_INCREMENT reset.
    Also clears TOKEN_FILE to avoid auth leakage.
    """
    # Remove persisted token between tests
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

    connection = db_engine.connect()
    Session = sessionmaker(bind=connection)
    session = Session()

    session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))

    tables = [
        "event",
        "contract",
        "client",
        "employee",
        "department",
    ]

    for table in tables:
        session.execute(text(f"TRUNCATE TABLE {table};"))

    session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
    session.commit()

    yield session

    session.close()
    connection.close()
