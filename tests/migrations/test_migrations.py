import pytest
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command
import os
import time

@pytest.fixture(scope="function")
def database_url():
    return os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test_db")

@pytest.fixture(scope="function")
def engine(database_url):
    return create_engine(database_url)

@pytest.fixture(scope="function")
def alembic_config():
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url())
    return config

def test_migration_applies_successfully(engine, alembic_config):
    """Test that migrations can be applied successfully"""
    command.upgrade(alembic_config, "head")
    
    # Verify the migration was applied
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar()
        assert version is not None

def test_migration_rollback(engine, alembic_config):
    """Test that migrations can be rolled back successfully"""
    # First apply migrations
    command.upgrade(alembic_config, "head")
    
    # Then rollback one step
    command.downgrade(alembic_config, "-1")
    
    # Verify we're at the previous version
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar()
        assert version is not None

@pytest.mark.benchmark
def test_migration_performance(engine, alembic_config, benchmark):
    """Test the performance impact of migrations"""
    def run_migration():
        command.upgrade(alembic_config, "head")
        command.downgrade(alembic_config, "base")
    
    # Measure the time taken for migration
    result = benchmark(run_migration)
    
    # Assert that migration completes within acceptable time (e.g., 5 seconds)
    assert result.seconds < 5.0

def test_data_integrity(engine, alembic_config):
    """Test that data remains intact after migration"""
    # Insert test data
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS test_table (id serial PRIMARY KEY, data text)"))
        conn.execute(text("INSERT INTO test_table (data) VALUES ('test_data')"))
        conn.commit()
    
    # Run migration
    command.upgrade(alembic_config, "head")
    
    # Verify data is intact
    with engine.connect() as conn:
        result = conn.execute(text("SELECT data FROM test_table")).scalar()
        assert result == 'test_data'

def test_concurrent_operations(engine, alembic_config):
    """Test that the database remains available during migration"""
    def background_operations():
        with engine.connect() as conn:
            for _ in range(10):
                conn.execute(text("SELECT 1"))
                time.sleep(0.1)
    
    # Start background operations
    import threading
    bg_thread = threading.Thread(target=background_operations)
    bg_thread.start()
    
    # Run migration
    command.upgrade(alembic_config, "head")
    
    # Wait for background operations to complete
    bg_thread.join()
    
    # If we got here without exceptions, the test passed 