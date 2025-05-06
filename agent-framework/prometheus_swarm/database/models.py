from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class Evidence:
    """
    Represents a piece of evidence in the system.
    Ensures uniqueness through hash value.
    """
    submission_id: str
    content: str
    hash_value: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """
        Validate evidence attributes upon initialization.
        """
        if not self.submission_id or not self.content or not self.hash_value:
            raise ValueError("Submission ID, content, and hash value are required.")

@dataclass
class Database:
    """
    Database management class with evidence tracking and uniqueness enforcement.
    """
    _evidence_store: dict = field(default_factory=dict)
    _evidence_by_submission: dict = field(default_factory=dict)

    def add_evidence(self, evidence: Evidence):
        """
        Add evidence with hash uniqueness constraint.
        
        Args:
            evidence (Evidence): Evidence to be added
        
        Raises:
            ValueError: If evidence with same hash already exists
        """
        if evidence.hash_value in self._evidence_store:
            raise ValueError("Evidence with this hash already exists")

        self._evidence_store[evidence.hash_value] = evidence

        # Track evidence by submission ID
        if evidence.submission_id not in self._evidence_by_submission:
            self._evidence_by_submission[evidence.submission_id] = []
        self._evidence_by_submission[evidence.submission_id].append(evidence)

    def get_evidence_by_hash(self, hash_value: str) -> Optional[Evidence]:
        """
        Retrieve evidence by hash value.
        
        Args:
            hash_value (str): Hash to search for
        
        Returns:
            Optional[Evidence]: Evidence if found, None otherwise
        """
        return self._evidence_store.get(hash_value)

    def get_evidence_by_submission_id(self, submission_id: str) -> List[Evidence]:
        """
        Retrieve all evidence for a given submission ID.
        
        Args:
            submission_id (str): Submission ID to search for
        
        Returns:
            List[Evidence]: List of evidence for the submission
        """
        return self._evidence_by_submission.get(submission_id, [])

    def get_all_evidence(self) -> List[Evidence]:
        """
        Retrieve all evidence in the system.
        
        Returns:
            List[Evidence]: All evidence entries
        """
        return list(self._evidence_store.values())

    def update_evidence(self, hash_value: str, new_content: Optional[str] = None):
        """
        Update evidence, with restrictions.
        
        Args:
            hash_value (str): Hash of evidence to update
            new_content (Optional[str]): New content for the evidence
        
        Raises:
            ValueError: If evidence cannot be modified
        """
        evidence = self.get_evidence_by_hash(hash_value)
        if not evidence:
            raise ValueError("Evidence not found")
        
        raise ValueError("Cannot modify existing evidence")  # Enforce immutability