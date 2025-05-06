import os
import sqlite3
from typing import List, Dict, Any, Optional

class DatabaseMigrator:
    """
    A class to handle database migrations with version tracking.
    
    This migrator helps manage schema changes for SQLite databases 
    by tracking and applying migration scripts in a sequential manner.
    """

    def __init__(self, db_path: str, migrations_dir: str = 'migrations'):
        """
        Initialize the DatabaseMigrator.

        Args:
            db_path (str): Path to the SQLite database file
            migrations_dir (str, optional): Directory containing migration scripts. Defaults to 'migrations'.
        """
        self.db_path = db_path
        self.migrations_dir = migrations_dir
        self._ensure_migrations_table()

    def _ensure_migrations_table(self):
        """
        Create a migrations tracking table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def get_applied_migrations(self) -> List[str]:
        """
        Retrieve a list of already applied migration versions.

        Returns:
            List[str]: List of migration versions that have been applied
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT version FROM schema_migrations')
            return [row[0] for row in cursor.fetchall()]

    def get_pending_migrations(self) -> List[str]:
        """
        Find migration scripts that have not yet been applied.

        Returns:
            List[str]: List of pending migration versions
        """
        applied_migrations = set(self.get_applied_migrations())
        migration_files = [f for f in os.listdir(self.migrations_dir) if f.endswith('.sql')]
        pending_migrations = [
            migration[:-4] for migration in migration_files 
            if migration[:-4] not in applied_migrations
        ]
        return sorted(pending_migrations)

    def apply_migration(self, version: str):
        """
        Apply a specific migration script.

        Args:
            version (str): Version of the migration to apply

        Raises:
            FileNotFoundError: If migration script is not found
            sqlite3.Error: If there's an error executing the migration
        """
        migration_path = os.path.join(self.migrations_dir, f'{version}.sql')
        
        if not os.path.exists(migration_path):
            raise FileNotFoundError(f'Migration script {version} not found')

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Read migration script
            with open(migration_path, 'r') as migration_file:
                migration_script = migration_file.read()

            # Execute migration
            cursor.executescript(migration_script)

            # Record migration
            cursor.execute(
                'INSERT INTO schema_migrations (version) VALUES (?)', 
                (version,)
            )
            conn.commit()

    def migrate(self, target_version: Optional[str] = None):
        """
        Run all pending migrations or migrations up to a specific version.

        Args:
            target_version (str, optional): Specific version to migrate to. 
                                            If None, applies all pending migrations.
        """
        pending_migrations = self.get_pending_migrations()
        
        if target_version:
            pending_migrations = [
                migration for migration in pending_migrations 
                if migration <= target_version
            ]

        for migration in pending_migrations:
            self.apply_migration(migration)

    def rollback(self, steps: int = 1):
        """
        Rollback recent migrations.

        Args:
            steps (int, optional): Number of migrations to rollback. Defaults to 1.

        Raises:
            ValueError: If no migrations have been applied or steps exceed applied migrations
        """
        applied_migrations = self.get_applied_migrations()
        
        if not applied_migrations:
            raise ValueError("No migrations to rollback")
        
        if steps > len(applied_migrations):
            raise ValueError(f"Cannot rollback {steps} migrations. Only {len(applied_migrations)} applied.")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for version in reversed(applied_migrations[-steps:]):
                # Rollback logic would typically involve running a .down.sql script
                # This is a placeholder. Implement specific rollback logic as needed.
                cursor.execute('DELETE FROM schema_migrations WHERE version = ?', (version,))
            
            conn.commit()