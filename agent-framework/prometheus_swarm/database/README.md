# Database Models

## Overview
This module contains SQLModel database models for tracking various aspects of system operations.

## Models

### TransactionTracking
The `TransactionTracking` model provides comprehensive transaction tracking capabilities:

- **Purpose**: Monitor and trace system transactions with detailed metadata
- **Key Features**:
  - Unique transaction ID
  - Transaction status tracking
  - Error and retry management
  - Timestamp tracking
  - Payload and metadata storage

#### Use Cases
- Track long-running processes
- Monitor system workflows
- Debug and audit transaction lifecycles
- Implement retry mechanisms

#### Example Usage
```python
transaction = TransactionTracking.create_transaction(
    transaction_id="unique_id_123",
    source="system_module",
    destination="external_service",
    payload_type="json",
    payload_size=1024
)
transaction.status = "PROCESSING"
# Later update with results
transaction.status = "COMPLETED"
```