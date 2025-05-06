import os
import sqlite3
import pytest
from src.database_migration import DatabaseMigration

@pytest.fixture
def migration_instance():
    """Create a DatabaseMigration instance for testing."""
    test_migration_db = 'test_migrations.db'
    if os.path.exists(test_migration_db):
        os.remove(test_migration_db)
    
    migration = DatabaseMigration(test_migration_db)
    yield migration
    
    # Clean up
    if os.path.exists(test_migration_db):
        os.remove(test_migration_db)

@pytest.fixture
def migrations_dir():
    """Ensure migrations directory exists."""
    migrations_dir = 'migrations'
    os.makedirs(migrations_dir, exist_ok=True)
    yield migrations_dir
    
    # Clean up migration files
    for file in os.listdir(migrations_dir):
        os.remove(os.path.join(migrations_dir, file))
    os.rmdir(migrations_dir)

def test_create_migration(migration_instance, migrations_dir):
    """Test creating a migration file."""
    result = migration_instance.create_migration(
        'create_users_table', 
        'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);',
        'DROP TABLE IF EXISTS users;'
    )
    assert result is True
    
    # Check migration file was created
    migration_files = os.listdir(migrations_dir)
    assert len(migration_files) == 1
    assert migration_files[0].endswith('_migration.sql')
    assert 'create_users_table' in migration_files[0]

def test_create_migration_invalid_name(migration_instance):
    """Test creating a migration with an invalid name."""
    with pytest.raises(ValueError):
        migration_instance.create_migration(
            'invalid-name', 
            'CREATE TABLE test (id INTEGER);',
            'DROP TABLE test;'
        )

def test_apply_migrations(migration_instance, migrations_dir):
    """Test applying migrations to a target database."""
    # Create test migrations
    migration_instance.create_migration(
        'create_users_table', 
        'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);',
        'DROP TABLE IF EXISTS users;'
    )
    
    target_db = 'test_target.db'
    if os.path.exists(target_db):
        os.remove(target_db)
    
    # Apply migrations
    applied = migration_instance.apply_migrations(target_db)
    assert len(applied) == 1
    assert 'create_users_table' in applied
    
    # Verify migration was applied
    with sqlite3.connect(target_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        assert cursor.fetchone() is not None
    
    # Clean up
    if os.path.exists(target_db):
        os.remove(target_db)

def test_rollback_migration(migration_instance, migrations_dir):
    """Test rolling back the last migration."""
    # Create and apply test migration
    migration_instance.create_migration(
        'create_users_table', 
        'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);',
        'DROP TABLE IF EXISTS users;'
    )
    
    target_db = 'test_target.db'
    if os.path.exists(target_db):
        os.remove(target_db)
    
    # Apply migrations
    migration_instance.apply_migrations(target_db)
    
    # Verify table exists
    with sqlite3.connect(target_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        assert cursor.fetchone() is not None
    
    # Rollback migration
    rolled_back = migration_instance.rollback_last_migration(target_db)
    assert rolled_back == 'create_users_table'
    
    # Verify table no longer exists
    with sqlite3.connect(target_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        assert cursor.fetchone() is None
    
    # Clean up
    if os.path.exists(target_db):
        os.remove(target_db)