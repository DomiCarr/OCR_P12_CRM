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
    Uses a JOINED transaction to allow rollback even after commits.
    """
    connection = db_engine.connect()
    # Begin a root transaction
    transaction = connection.begin()

    # Bind the session to the connection with join_transaction=True
    session = sessionmaker()(bind=connection, join_transaction=True)

    yield session

    session.close()
    # Rollback everything, including what was "committed" during the test
    transaction.rollback()
    connection.close()