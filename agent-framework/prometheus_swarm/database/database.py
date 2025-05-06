import sqlite3
from typing import Dict, Any, Optional
from .models import Evidence

class Database:
    """Database class for managing evidence storage and retrieval."""

    def __init__(self, db_path: str = 'evidence.db'):
        """
        Initialize the database connection.
        
        Args:
            db_path (str): Path to the SQLite database file. Defaults to 'evidence.db'.
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish a connection to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            self._create_tables()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error connecting to database: {e}")

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS evidence (
                    identifier TEXT PRIMARY KEY,
                    content TEXT,
                    source TEXT,
                    additional_metadata TEXT
                )
            ''')
            self.connection.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Error creating tables: {e}")

    def insert_evidence(self, evidence: Evidence):
        """
        Insert a new evidence entry into the database.
        
        Args:
            evidence (Evidence): The evidence to be inserted.
        
        Raises:
            ValueError: If evidence with the same identifier already exists.
        """
        try:
            import json
            
            # Check if evidence with the same identifier already exists
            existing = self.get_evidence_by_identifier(evidence.identifier)
            if existing:
                raise ValueError(f"Evidence with identifier '{evidence.identifier}' already exists")

            metadata_json = json.dumps(evidence.additional_metadata) if evidence.additional_metadata else None
            
            self.cursor.execute('''
                INSERT INTO evidence (identifier, content, source, additional_metadata)
                VALUES (?, ?, ?, ?)
            ''', (evidence.identifier, evidence.content, evidence.source, metadata_json))
            
            self.connection.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Duplicate evidence identifier: {evidence.identifier}")
        except sqlite3.Error as e:
            raise RuntimeError(f"Error inserting evidence: {e}")

    def get_evidence_by_identifier(self, identifier: str) -> Optional[Evidence]:
        """
        Retrieve an evidence entry by its identifier.
        
        Args:
            identifier (str): The unique identifier of the evidence.
        
        Returns:
            Evidence or None: The evidence if found, otherwise None.
        """
        try:
            import json
            
            self.cursor.execute('SELECT * FROM evidence WHERE identifier = ?', (identifier,))
            result = self.cursor.fetchone()
            
            if result:
                identifier, content, source, metadata_str = result
                additional_metadata = json.loads(metadata_str) if metadata_str else None
                
                return Evidence(
                    identifier=identifier,
                    content=content,
                    source=source,
                    additional_metadata=additional_metadata
                )
            
            return None
        except sqlite3.Error as e:
            raise RuntimeError(f"Error retrieving evidence: {e}")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None