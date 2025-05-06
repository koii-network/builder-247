import asyncio
import pytest
from prometheus_swarm.transaction_id_concurrency import TransactionIDManager

@pytest.mark.asyncio
async def test_unique_transaction_id_generation():
    """
    Test that transaction IDs are generated uniquely in a concurrent environment.
    """
    transaction_manager = TransactionIDManager()
    
    # Generate multiple transaction IDs concurrently
    num_ids = 1000
    transaction_ids = await asyncio.gather(
        *[transaction_manager.generate_unique_transaction_id() for _ in range(num_ids)]
    )
    
    # Ensure all IDs are unique
    assert len(set(transaction_ids)) == num_ids
    assert None not in transaction_ids

@pytest.mark.asyncio
async def test_concurrent_transaction_submission():
    """
    Test concurrent transaction submissions to ensure thread safety.
    """
    transaction_manager = TransactionIDManager()
    
    # Create a transaction ID
    transaction_id = await transaction_manager.generate_unique_transaction_id()
    
    # Simulate concurrent submissions
    submission_results = await asyncio.gather(
        transaction_manager.submit_transaction(transaction_id),
        transaction_manager.submit_transaction(transaction_id)
    )
    
    # Ensure only first submission succeeds
    assert submission_results.count(True) == 1
    assert submission_results.count(False) == 1

@pytest.mark.asyncio
async def test_transaction_id_collision_prevention():
    """
    Test that the manager prevents transaction ID collisions.
    """
    transaction_manager = TransactionIDManager()
    
    # Generate multiple transaction IDs and try to reuse them
    transaction_ids = [
        await transaction_manager.generate_unique_transaction_id() 
        for _ in range(100)
    ]
    
    # Attempt to submit duplicate transaction IDs
    duplicate_submissions = await asyncio.gather(
        *[transaction_manager.submit_transaction(tid) for tid in transaction_ids] +
        *[transaction_manager.submit_transaction(tid) for tid in transaction_ids]
    )
    
    # First set of submissions should all be True
    first_half = duplicate_submissions[:len(transaction_ids)]
    assert all(first_half), "First submissions should all succeed"
    
    # Second set of submissions should all be False
    second_half = duplicate_submissions[len(transaction_ids):]
    assert all(not result for result in second_half), "Duplicate submissions should fail"

@pytest.mark.asyncio
async def test_transaction_reset():
    """
    Test resetting transaction IDs.
    """
    transaction_manager = TransactionIDManager()
    
    # Generate and submit a transaction
    transaction_id = await transaction_manager.generate_unique_transaction_id()
    await transaction_manager.submit_transaction(transaction_id)
    
    # Reset transactions
    await transaction_manager.reset_transactions()
    
    # Resubmit should now succeed
    result = await transaction_manager.submit_transaction(transaction_id)
    assert result is True, "Transaction should be submittable after reset"