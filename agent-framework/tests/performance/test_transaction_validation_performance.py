"""Performance testing for transaction ID validation."""

import timeit
import uuid
from prometheus_swarm.utils.transaction_validation import validate_transaction_id

def test_validation_performance():
    """Ensure transaction ID validation completes within 50ms."""
    def validate_single_transaction():
        transaction_id = str(uuid.uuid4())
        validate_transaction_id(transaction_id)

    # Run multiple iterations to get a reliable average
    execution_time = timeit.timeit(validate_single_transaction, number=1000) / 1000
    
    # Convert to milliseconds
    execution_time_ms = execution_time * 1000
    
    print(f"\nAverage Validation Time: {execution_time_ms:.4f} ms")
    assert execution_time_ms < 50, f"Validation took {execution_time_ms:.4f} ms, which exceeds 50ms limit"