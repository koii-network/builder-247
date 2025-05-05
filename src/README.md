# Transaction ID Cleanup Module

## Overview
This module provides a robust solution for cleaning and standardizing transaction IDs. The `clean_transaction_id()` function ensures that transaction IDs:
- Are consistent in format
- Have special characters removed
- Are converted to lowercase
- Have a maximum length
- Generate a unique identifier if input is invalid

## Features
- Removes leading/trailing whitespace
- Strips out non-alphanumeric characters (except hyphens)
- Converts to lowercase
- Truncates to 50 characters
- Generates a UUID for empty or invalid inputs

## Usage Example
```python
from src.transaction_cleanup import clean_transaction_id

# Basic usage
cleaned_id = clean_transaction_id("  Transaction123!  ")
print(cleaned_id)  # Outputs: "transaction123"

# Handling invalid input
try:
    cleaned_id = clean_transaction_id("")
except ValueError as e:
    print(f"Error: {e}")
```

## Error Handling
- Raises `ValueError` for `None` or empty inputs
- Generates a unique UUID for inputs that become empty after cleaning