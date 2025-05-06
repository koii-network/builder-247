import os
import sqlite3
from typing import List, Dict, Any, Optional

class DatabaseMigration:
    """
    A utility class for managing database schema migrations.
    
    This class provides methods to:
    - Create migration files
    - Apply migrations
    - Rollback migrations
    - Track migration history
    """
    
    def __init__(self, db_path: str = 'migrations.db'):
        """
        Initialize the DatabaseMigration instance.
        
        Args:
            db_path (str): Path to the SQLite database for tracking migrations
        """
        self.db_path = db_path
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """
        Create a migrations tracking table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def create_migration(self, name: str, up_sql: str, down_sql: str) -> bool:
        """
        Create a new migration file.
        
        Args:
            name (str): Name of the migration
            up_sql (str): SQL to apply the migration
            down_sql (str): SQL to rollback the migration
        
        Returns:
            bool: True if migration file created successfully
        """
        if not name or not name.isidentifier():
            raise ValueError("Migration name must be a valid Python identifier")
        
        migrations_dir = 'migrations'
        os.makedirs(migrations_dir, exist_ok=True)
        
        migration_file = os.path.join(migrations_dir, f"{name}_migration.sql")
        with open(migration_file, 'w') as f:
            f.write(f"-- Up Migration:\n{up_sql}\n\n-- Down Migration:\n{down_sql}")
        
        return True
    
    def apply_migrations(self, target_db_path: str) -> List[str]:
        """
        Apply all pending migrations to the target database.
        
        Args:
            target_db_path (str): Path to the target database
        
        Returns:
            List[str]: List of applied migration names
        """
        applied_migrations = []
        migrations_dir = 'migrations'
        
        if not os.path.exists(migrations_dir):
            return applied_migrations
        
        with sqlite3.connect(self.db_path) as migration_conn, \
             sqlite3.connect(target_db_path) as target_conn:
            
            migration_cursor = migration_conn.cursor()
            target_cursor = target_conn.cursor()
            
            for migration_file in sorted(os.listdir(migrations_dir)):
                if not migration_file.endswith('_migration.sql'):
                    continue
                
                migration_name = os.path.splitext(migration_file)[0].replace('_migration', '')
                
                # Check if migration has already been applied
                migration_cursor.execute(
                    'SELECT COUNT(*) FROM migrations WHERE name = ?', 
                    (migration_name,)
                )
                if migration_cursor.fetchone()[0] > 0:
                    continue
                
                # Read migration file
                with open(os.path.join(migrations_dir, migration_file), 'r') as f:
                    migration_content = f.read()
                
                # Extract up migration SQL
                up_sql = migration_content.split('-- Up Migration:')[1].split('-- Down Migration:')[0].strip()
                
                # Apply migration
                target_cursor.executescript(up_sql)
                
                # Record migration
                migration_cursor.execute(
                    'INSERT INTO migrations (name) VALUES (?)', 
                    (migration_name,)
                )
                
                applied_migrations.append(migration_name)
            
            migration_conn.commit()
            target_conn.commit()
        
        return applied_migrations
    
    def rollback_last_migration(self, target_db_path: str) -> Optional[str]:
        """
        Rollback the last applied migration.
        
        Args:
            target_db_path (str): Path to the target database
        
        Returns:
            Optional[str]: Name of the rolled back migration, or None if no migrations
        """
        with sqlite3.connect(self.db_path) as migration_conn, \
             sqlite3.connect(target_db_path) as target_conn:
            
            migration_cursor = migration_conn.cursor()
            target_cursor = target_conn.cursor()
            
            # Get the last applied migration
            migration_cursor.execute(
                'SELECT name FROM migrations ORDER BY applied_at DESC LIMIT 1'
            )
            result = migration_cursor.fetchone()
            
            if not result:
                return None
            
            migration_name = result[0]
            migrations_dir = 'migrations'
            migration_file = os.path.join(migrations_dir, f"{migration_name}_migration.sql")
            
            # Read migration file
            with open(migration_file, 'r') as f:
                migration_content = f.read()
            
            # Extract down migration SQL
            down_sql = migration_content.split('-- Down Migration:')[1].strip()
            
            # Apply down migration
            target_cursor.executescript(down_sql)
            
            # Remove migration record
            migration_cursor.execute(
                'DELETE FROM migrations WHERE name = ?', 
                (migration_name,)
            )
            
            migration_conn.commit()
            target_conn.commit()
        
        return migration_name