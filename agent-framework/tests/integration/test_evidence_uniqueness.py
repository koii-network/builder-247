import pytest
from prometheus_swarm.database.database import Database
from prometheus_swarm.database.models import Evidence
from typing import List

class TestEvidenceUniqueness:
    """
    Integration tests to ensure evidence uniqueness across different scenarios.
    """

    @pytest.fixture
    def db(self):
        """Create a fresh database for each test."""
        return Database()

    def test_add_unique_evidence(self, db):
        """
        Test that unique evidence can be added successfully.
        """
        evidence1 = Evidence(
            submission_id="test_submission_1",
            content="First unique evidence content",
            hash_value="hash1"
        )
        evidence2 = Evidence(
            submission_id="test_submission_2", 
            content="Second unique evidence content",
            hash_value="hash2"
        )

        db.add_evidence(evidence1)
        db.add_evidence(evidence2)

        all_evidence = db.get_all_evidence()
        assert len(all_evidence) == 2, "Failed to add unique evidence"

    def test_prevent_duplicate_hash_evidence(self, db):
        """
        Test that evidence with duplicate hash cannot be added.
        """
        evidence1 = Evidence(
            submission_id="test_submission_1",
            content="First evidence content",
            hash_value="unique_hash"
        )
        evidence2 = Evidence(
            submission_id="test_submission_2", 
            content="Duplicate hash evidence",
            hash_value="unique_hash"  # Same hash as evidence1
        )

        db.add_evidence(evidence1)
        
        with pytest.raises(ValueError, match="Evidence with this hash already exists"):
            db.add_evidence(evidence2)

    def test_evidence_retrieval_by_hash(self, db):
        """
        Test retrieving evidence by hash value.
        """
        evidence1 = Evidence(
            submission_id="test_submission_1",
            content="First evidence content",
            hash_value="specific_hash"
        )

        db.add_evidence(evidence1)
        retrieved_evidence = db.get_evidence_by_hash("specific_hash")

        assert retrieved_evidence is not None, "Failed to retrieve evidence by hash"
        assert retrieved_evidence.hash_value == "specific_hash"

    def test_multiple_evidence_for_same_submission(self, db):
        """
        Test adding multiple evidence for the same submission, ensuring hash uniqueness.
        """
        evidence_items: List[Evidence] = [
            Evidence(
                submission_id="test_submission_1",
                content=f"Evidence content {i}",
                hash_value=f"hash_{i}"
            ) for i in range(3)
        ]

        for evidence in evidence_items:
            db.add_evidence(evidence)

        retrieved_evidence = db.get_evidence_by_submission_id("test_submission_1")
        assert len(retrieved_evidence) == 3, "Failed to add multiple evidence for same submission"

    def test_evidence_update_restrictions(self, db):
        """
        Test restrictions on updating existing evidence.
        """
        evidence1 = Evidence(
            submission_id="test_submission_1",
            content="Original evidence content",
            hash_value="update_hash"
        )

        db.add_evidence(evidence1)

        with pytest.raises(ValueError, match="Cannot modify existing evidence"):
            db.update_evidence("update_hash", new_content="Modified content")