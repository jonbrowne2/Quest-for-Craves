import os
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from recipe_value_system.config import DatabaseConfig, RedisConfig, SystemConfig

# Import models here to avoid circular dependencies
from recipe_value_system.models import Base


# Fixing first line docstring issues and unused imports
@pytest.fixture(scope="session")
def test_config() -> SystemConfig:
    """Create test configuration"""
    # Set test environment variables
    os.environ["DB_URL"] = "sqlite:///test.db"
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["APP_ENV"] = "test"

    return SystemConfig()


@pytest.fixture(scope="session")
def db_engine(test_config):
    """Create test database engine"""
    engine = create_engine(test_config.db.URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine) -> Generator:
    """Create test database session"""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def redis_client(test_config) -> Generator:
    """Create test redis client"""
    client = redis.Redis(
        host=test_config.redis.HOST,
        port=test_config.redis.PORT,
        decode_responses=True,
        db=15,  # Use separate database for testing
    )
    yield client
    client.flushdb()  # Clean up after tests
