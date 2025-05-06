import os
import sqlite3
import pytest
import tempfile
import shutil
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from prometheus_swarm.database.migration import DatabaseMigrator

@pytest.fixture
def temp_migrations_dir():
    """Create a temporary directory for migration scripts."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_db:
        db_path = temp_db.name
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)

def test_ensure_migrations_table(temp_db_path, temp_migrations_dir):
    """Test that migrations table is created automatically."""
    migrator = DatabaseMigrator(temp_db_path, temp_migrations_dir)
    
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
        assert cursor.fetchone() is not None

def test_get_applied_migrations(temp_db_path, temp_migrations_dir):
    """Test retrieving applied migrations."""
    migrator = DatabaseMigrator(temp_db_path, temp_migrations_dir)
    
    # Initially no migrations should be applied
    assert migrator.get_applied_migrations() == []

def test_pending_migrations(temp_db_path, temp_migrations_dir):
    """Test retrieving pending migrations."""
    # Create mock migration scripts
    migration_scripts = [
        '001_initial_schema.sql',
        '002_add_users.sql',
        '003_add_indexes.sql'
    ]
    
    for script in migration_scripts:
        with open(os.path.join(temp_migrations_dir, script), 'w') as f:
            f.write("-- Test migration")
    
    migrator = DatabaseMigrator(temp_db_path, temp_migrations_dir)
    pending = migrator.get_pending_migrations()
    
    assert set(pending) == {'001_initial_schema', '002_add_users', '003_add_indexes'}

def test_apply_migration(temp_db_path, temp_migrations_dir):
    """Test applying a single migration."""
    # Create a test migration script
    migration_script = '''
    CREATE TABLE test_table (
        id INTEGER PRIMARY KEY,
        name TEXT
    );
    '''
    
    with open(os.path.join(temp_migrations_dir, '001_create_test_table.sql'), 'w') as f:
        f.write(migration_script)
    
    migrator = DatabaseMigrator(temp_db_path, temp_migrations_dir)
    migrator.apply_migration('001_create_test_table')
    
    # Verify migration was recorded
    applied_migrations = migrator.get_applied_migrations()
    assert '001_create_test_table' in applied_migrations
    
    # Verify table was created
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
        assert cursor.fetchone() is not None

def test_apply_non_existent_migration(temp_db_path, temp_migrations_dir):
    """Test applying a non-existent migration raises an error."""
    migrator = DatabaseMigrator(temp_db_path, temp_migrations_dir)
    
    with pytest.raises(FileNotFoundError):
        migrator.apply_migration('non_existent_migration')

def test_migrate_all_pending(temp_db_path, temp_migrations_dir):
    """Test migrating all pending migrations."""
    # Create multiple migration scripts
    migration_scripts = {
        '001_initial_schema.sql': 'CREATE TABLE users (id INTEGER PRIMARY KEY);',
        '002_add_email.sql': 'ALTER TABLE users ADD COLUMN email TEXT;',
        '003_add_active_flag.sql': 'ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;'
    }
    
    for name, script in migration_scripts.items():
        with open(os.path.join(temp_migrations_dir, name), 'w') as f:
            f.write(script)
    
    migrator = DatabaseMigrator(temp_db_path, temp_migrations_dir)
    migrator.migrate()
    
    # Verify all migrations were applied
    applied_migrations = migrator.get_applied_migrations()
    assert set(applied_migrations) == {
        '001_initial_schema', 
        '002_add_email', 
        '003_add_active_flag'
    }

def test_migrate_to_specific_version(temp_db_path, temp_migrations_dir):
    """Test migrating to a specific version."""
    migration_scripts = {
        '001_initial_schema.sql': 'CREATE TABLE users (id INTEGER PRIMARY KEY);',
        '002_add_email.sql': 'ALTER TABLE users ADD COLUMN email TEXT;',
        '003_add_active_flag.sql': 'ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1;'
    }
    
    for name, script in migration_scripts.items():
        with open(os.path.join(temp_migrations_dir, name), 'w') as f:
            f.write(script)
    
    migrator = DatabaseMigrator(temp_db_path, temp_migrations_dir)
    migrator.migrate('002_add_email')
    
    applied_migrations = migrator.get_applied_migrations()
    assert set(applied_migrations) == {'001_initial_schema', '002_add_email'}

def test_rollback(temp_db_path, temp_migrations_dir):
    """Test rolling back migrations."""
    migration_scripts = {
        '001_initial_schema.sql': 'CREATE TABLE users (id INTEGER PRIMARY KEY);',
        '002_add_email.sql': 'ALTER TABLE users ADD COLUMN email TEXT;'
    }
    
    for name, script in migration_scripts.items():
        with open(os.path.join(temp_migrations_dir, name), 'w') as f:
            f.write(script)
    
    migrator = DatabaseMigrator(temp_db_path, temp_migrations_dir)
    migrator.migrate()
    
    # Rollback one step
    migrator.rollback()
    
    applied_migrations = migrator.get_applied_migrations()
    assert applied_migrations == ['001_initial_schema']

def test_rollback_no_migrations(temp_db_path, temp_migrations_dir):
    """Test rolling back when no migrations exist."""
    migrator = DatabaseMigrator(temp_db_path, temp_migrations_dir)
    
    with pytest.raises(ValueError, match="No migrations to rollback"):
        migrator.rollback()