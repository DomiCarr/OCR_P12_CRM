# tests/conftest.py
"""
Pytest configuration and global fixtures.
Provides database engine and session management for tests.

Tests included:
- N/A (Configuration file)

Changes:
- Removed unused 'os' import to satisfy flake8.
- Added load_dotenv() to ensure environment variables are available.
"""

from dotenv import load_dotenv
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import Config

# Load environment variables from .env file at startup
load_dotenv()


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
    # Start a transaction
    transaction = connection.begin()

    # Bind session to connection
    Session = sessionmaker(bind=connection)
    session = Session()

    # Create a SAVEPOINT to allow sub-transactions (commits in tests)
    nested = connection.begin_nested()

    @pytest.fixture
    def _rollback_nested():
        yield
        if nested.is_active:
            nested.rollback()

    yield session

    session.close()
    # Rollback the root transaction to undo everything
    transaction.rollback()
    connection.close()
    connection.close()