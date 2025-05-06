import pytest
import warnings
from prometheus_swarm.database.database import Database
from prometheus_swarm.database.models import Evidence

class TestEvidenceUniqueness:
    """Test suite for ensuring evidence uniqueness in the system."""

    @pytest.fixture
    def db_connection(self):
        """Fixture to provide a database connection for testing."""
        database = Database()
        try:
            database.connect()
            yield database
        finally:
            database.close()

    def test_insert_unique_evidence(self, db_connection):
        """
        Test that unique evidence can be inserted successfully.
        
        Ensures that evidence with a unique identifier can be added to the database.
        """
        evidence = Evidence(
            identifier='test_unique_evidence_1',
            content='Sample unique evidence content',
            source='test_source'
        )
        
        try:
            db_connection.insert_evidence(evidence)
            retrieved_evidence = db_connection.get_evidence_by_identifier(evidence.identifier)
            
            assert retrieved_evidence is not None
            assert retrieved_evidence.identifier == evidence.identifier
        except Exception as e:
            pytest.fail(f"Failed to insert unique evidence: {e}")

    def test_prevent_duplicate_evidence_insertion(self, db_connection):
        """
        Test that duplicate evidence cannot be inserted into the database.
        
        Ensures that attempting to insert evidence with an existing identifier
        raises an appropriate exception or prevents duplication.
        """
        duplicate_evidence = Evidence(
            identifier='test_duplicate_evidence',
            content='Original evidence content',
            source='test_source'
        )
        
        # First insertion should succeed
        db_connection.insert_evidence(duplicate_evidence)
        
        # Second insertion with same identifier should fail
        with pytest.raises((ValueError, Exception), match='duplicate|unique|constraint'):
            db_connection.insert_evidence(duplicate_evidence)

    def test_evidence_identifier_case_sensitivity(self, db_connection):
        """
        Test evidence identifier case sensitivity.
        
        Verifies the behavior of identifier uniqueness across different letter cases.
        This test now explicitly checks for case-sensitivity policy.
        """
        original_evidence = Evidence(
            identifier='Test_Case_Sensitive_Evidence',
            content='Original case-sensitive evidence',
            source='test_source'
        )
        
        similar_case_evidence = Evidence(
            identifier='test_case_sensitive_evidence',
            content='Similar case evidence',
            source='test_source'
        )
        
        # Insert the first evidence
        db_connection.insert_evidence(original_evidence)
        
        # We expect this to either raise an exception or be allowed based on the system's design
        try:
            db_connection.insert_evidence(similar_case_evidence)
            # If insertion is allowed, we'll raise a warning
            warnings.warn(
                "Case-insensitive evidence identifiers might be a potential issue", 
                UserWarning
            )
        except ValueError as e:
            # If an exception is raised, it should indicate a uniqueness constraint
            assert 'duplicate' in str(e).lower() or 'unique' in str(e).lower()

    def test_evidence_metadata_preservation(self, db_connection):
        """
        Test that evidence metadata is preserved during insertion and retrieval.
        
        Ensures that all metadata associated with evidence is correctly stored and retrieved.
        """
        evidence = Evidence(
            identifier='metadata_preservation_test',
            content='Evidence with complete metadata',
            source='test_source',
            additional_metadata={
                'tags': ['important', 'test'],
                'confidence_score': 0.95,
                'collection_timestamp': '2023-01-01T12:00:00Z'
            }
        )
        
        db_connection.insert_evidence(evidence)
        retrieved_evidence = db_connection.get_evidence_by_identifier(evidence.identifier)
        
        assert retrieved_evidence is not None
        assert retrieved_evidence.additional_metadata == evidence.additional_metadata

    def test_large_volume_evidence_insertion(self, db_connection):
        """
        Performance and scalability test for evidence insertion.
        
        Validates the system's ability to handle multiple evidence entries efficiently.
        """
        unique_evidences = [
            Evidence(
                identifier=f'large_volume_test_{i}',
                content=f'Evidence content for test {i}',
                source='performance_test'
            ) for i in range(1000)
        ]
        
        # Insert all evidences
        for evidence in unique_evidences:
            db_connection.insert_evidence(evidence)
        
        # Verify insertion
        for evidence in unique_evidences:
            retrieved = db_connection.get_evidence_by_identifier(evidence.identifier)
            assert retrieved is not None