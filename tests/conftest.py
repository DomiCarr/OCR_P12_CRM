# tests/conftest.py
"""
Pytest configuration and global fixtures.
Provides database engine and session management for tests.
Initializes Sentry for error tracking during tests.
"""

from dotenv import load_dotenv
import pytest
import sentry_sdk
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import Config

# Load environment variables from .env file at startup
load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def init_sentry():
    """
    Initialize Sentry at the start of the test session.
    Ensures that capture_message and exceptions are sent to the dashboard.
    """
    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        environment="testing",
        traces_sample_rate=1.0
    )


@pytest.fixture(scope="session")
def db_engine():
    """
    Create a database engine for the test session.
    Uses the connection URL from the project configuration.
    """
    engine = create_engine(Config.get_db_url())
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Provide a clean database session for each test.
    Uses a nested transaction (SAVEPOINT) to allow rollback.
    """
    connection = db_engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    # Create a SAVEPOINT to allow sub-transactions (commits in tests)
    nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()