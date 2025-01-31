# Agent Testing Guide

This guide explains how to write and organize tests when implementing a todo item.

## Test Organization

### Test Location

- Place tests in the appropriate directory:
  - `tests/unit/` for testing individual components
  - `tests/integration/` for testing interactions between components
- Name test files to match the implementation: `test_<feature>.py`
- Follow the structure shown in `docs/test_template.py`

### Test Structure

1. **Group Related Tests by Feature**

   - Create a test class for each major feature/component
   - Name classes clearly: `TestFeatureName`, `TestAPIRateLimiting`, etc.
   - Use docstrings to explain what the group tests
   - List related test modules that test dependent functionality

2. **Test Categories Within Groups**
   - Core functionality tests first
   - Edge case tests
   - Error handling tests
   - Integration tests with related features

### Test Documentation

Every test function must have a docstring that explains:

1. What requirement(s) it verifies
2. Any assumptions or preconditions
3. Expected behavior
4. Related tests or dependencies

Example:

```python
def test_rate_limiting():
    """Verify API rate limiting behavior.

    Requirements:
    1. Requests should be limited to 100 per minute
    2. Excess requests should receive 429 response

    Assumptions:
    - API server is running
    - Rate limit is configured in settings
    """
```

## Writing Tests

### 1. Analyze Requirements

- Read and understand the acceptance criteria
- Break down into testable requirements
- Plan test scenarios for each requirement
- Consider dependencies between requirements

### 2. Setup Test Environment

- Import and use fixtures from `tests/utils/fixtures.py`
- Setup only what's needed for the specific test
- Document any required environment state
- Use class-level fixtures for shared setup

### 3. Write Test Cases

- Start with the most important scenarios:
  - Happy path tests that verify core functionality
  - Edge cases that could break the system
  - Error conditions that must be handled
  - Integration points with other components

Example:

```python
def test_successful_operation():
    """Verify normal operation succeeds.

    Requirements:
    1. Operation should complete successfully
    2. Result should match expected format
    """
    result = perform_operation()
    assert result.status == "success"
    assert isinstance(result.data, dict)

def test_invalid_input():
    """Verify handling of invalid input.

    Requirements:
    1. Should raise ValueError with clear message
    2. Should not modify any state
    """
    with pytest.raises(ValueError) as exc:
        perform_operation(invalid_input)
    assert "Invalid input" in str(exc.value)
```

### 4. Test Edge Cases

Common edge cases to consider:

- Empty/null inputs
- Boundary conditions
- Invalid formats
- Resource limitations
- Concurrent operations
- Network failures
- Timeout conditions

### 5. Integration Points

When testing features that interact:

- Verify data flow between components
- Test error propagation
- Check state consistency
- Test realistic usage scenarios

## Test Maintenance

### Handling Test Failures

When a test fails, analyze whether:

1. The implementation is incorrect
2. The test's expectations are wrong
3. Requirements have changed
4. There are conflicting requirements

Fix appropriately:

- Update implementation if it's a bug
- Update test if requirements changed
- Document why the change was needed

### Updating Tests

- Keep test documentation current
- Remove obsolete tests
- Update tests when requirements change
- Maintain test data and fixtures

## Important Notes for the LLM

1. Always read the full implementation before writing tests
2. Consider how features interact when writing integration tests
3. If tests conflict, identify which requirement takes precedence
4. Use docstrings to explain your test design decisions
5. When fixing failures, explain why you chose to fix the test vs the implementation
