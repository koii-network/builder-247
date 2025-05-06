import os
import sqlite3
import pytest
from prometheus_swarm.database.migration import perform_database_migration

def test_perform_database_migration_initial():
    """Test initial database migration creates schema_version and conversation_history tables"""
    # Temporary database path
    db_path = 'test_migration.db'
    
    try:
        # Perform migration
        result = perform_database_migration(db_path)
        assert result is True
        
        # Verify schema version table
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_version")
            version = cursor.fetchone()[0]
            assert version == 1
            
            # Verify conversation_history table exists
            cursor.execute("PRAGMA table_info(conversation_history)")
            columns = cursor.fetchall()
            assert len(columns) > 0
            
            # Check specific columns
            column_names = [col[1] for col in columns]
            assert "id" in column_names
            assert "timestamp" in column_names
            assert "model_name" in column_names
            assert "prompt" in column_names
            assert "response" in column_names
            assert "tokens_used" in column_names
            assert "status" in column_names
    
    finally:
        # Clean up the test database
        if os.path.exists(db_path):
            os.remove(db_path)

def test_migration_multiple_calls():
    """Test that multiple migrations don't cause issues"""
    db_path = 'test_migration_multiple.db'
    
    try:
        # First migration
        result1 = perform_database_migration(db_path)
        assert result1 is True
        
        # Second migration (should be a no-op)
        result2 = perform_database_migration(db_path)
        assert result2 is True
        
        # Verify schema version
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_version")
            version = cursor.fetchone()[0]
            assert version == 1
    
    finally:
        # Clean up the test database
        if os.path.exists(db_path):
            os.remove(db_path)

def test_migration_non_existent_path(tmpdir):
    """Test migration with a directory that doesn't exist"""
    # Use a path that's guaranteed to be unwritable
    import os.path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a read-only directory
        unwritable_dir = os.path.join(tmpdir, 'unwritable')
        os.makedirs(unwritable_dir)
        os.chmod(unwritable_dir, 0o555)  # Read and execute permissions only
        
        db_path = os.path.join(unwritable_dir, 'test.db')
        
        result = perform_database_migration(db_path)
        assert result is False