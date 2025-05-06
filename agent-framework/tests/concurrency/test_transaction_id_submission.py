import asyncio
import concurrent.futures
import pytest
from typing import List, Dict, Any
from unittest.mock import Mock, patch

class MockTransactionManager:
    def __init__(self):
        self._transaction_ids = set()
        self._lock = asyncio.Lock()

    async def submit_transaction_id(self, transaction_id: str) -> bool:
        """
        Submit a transaction ID with concurrency safety.
        
        Args:
            transaction_id (str): The transaction ID to submit
        
        Returns:
            bool: True if the transaction ID is unique and submitted, False otherwise
        """
        async with self._lock:
            if transaction_id in self._transaction_ids:
                return False
            self._transaction_ids.add(transaction_id)
            return True

class TestTransactionIDConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_transaction_id_submission(self):
        """
        Test concurrent transaction ID submissions to ensure:
        1. No duplicate transaction IDs are accepted
        2. Concurrent submissions are handled safely
        3. Thread/coroutine safety is maintained
        """
        transaction_manager = MockTransactionManager()
        
        # Generate a list of transaction IDs with some duplicates
        transaction_ids = [
            f"tx_{i}" for i in range(100)  # Many unique transactions
        ] + [
            f"tx_{i}" for i in range(50)  # Some duplicates to test race conditions
        ]
        
        # Run submissions concurrently
        async def submit_transaction(transaction_id):
            return await transaction_manager.submit_transaction_id(transaction_id)
        
        # Use asyncio to simulate concurrent submissions
        tasks = [submit_transaction(tx_id) for tx_id in transaction_ids]
        results = await asyncio.gather(*tasks)
        
        # Verify results
        unique_submissions = set()
        for tx_id, success in zip(transaction_ids, results):
            if success:
                assert tx_id not in unique_submissions, f"Duplicate transaction {tx_id} should not be allowed"
                unique_submissions.add(tx_id)
        
        # Ensure only unique transaction IDs were accepted
        assert len(unique_submissions) == len(set(transaction_ids[:100])), \
            "Not all unique transaction IDs were processed correctly"

    @pytest.mark.asyncio
    async def test_high_concurrency_transaction_submission(self):
        """
        Test high concurrency scenario with many parallel transaction submissions
        """
        transaction_manager = MockTransactionManager()
        
        # Large number of transactions with some duplicates
        transaction_ids = [
            f"high_concurrent_tx_{i % 50}" for i in range(1000)
        ]
        
        # Define submission coroutine
        async def submit_transaction(transaction_id):
            return await transaction_manager.submit_transaction_id(transaction_id)
        
        # Run submissions concurrently
        tasks = [submit_transaction(tx_id) for tx_id in transaction_ids]
        results = await asyncio.gather(*tasks)
        
        # Count unique first occurrences
        first_occurrences = {}
        for tx_id, success in zip(transaction_ids, results):
            if success and tx_id not in first_occurrences:
                first_occurrences[tx_id] = True
        
        # Verify only first submissions of each unique transaction are accepted
        assert len(first_occurrences) == 50, \
            "High concurrency test failed to handle duplicate transactions"

    @pytest.mark.asyncio
    async def test_thread_safe_transaction_submission(self):
        """
        Test thread-safe transaction ID submission across multiple threads
        """
        transaction_manager = MockTransactionManager()
        
        def thread_submission(thread_id):
            """Simulate thread-based transaction submissions"""
            tx_id = f"thread_tx_{thread_id}"
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
                transaction_manager.submit_transaction_id(tx_id)
            )
        
        # Use ThreadPoolExecutor to simulate concurrent thread submissions
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(thread_submission, i) for i in range(100)]
            
            # Wait for all submissions and collect results
            thread_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Verify thread-safe unique transaction submissions
        successful_submissions = sum(thread_results)
        assert successful_submissions == len(set(f"thread_tx_{i}" for i in range(100))), \
            "Thread-safe transaction submission failed"