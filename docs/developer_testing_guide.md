# Developer Testing Guide

This guide is for developers working on the implementation agent itself.

## Test Organization

### Directory Structure

```
tests/
  unit/           # Unit tests for individual components
  integration/    # Integration tests between components
  acceptance/     # End-to-end acceptance tests
  utils/          # Shared test utilities and fixtures
```

### Test Categories

1. **Unit Tests**

   - Test individual classes/functions in isolation
   - Mock external dependencies
   - Focus on edge cases and error handling
   - Example: `test_test_history.py`, `test_implementation_agent.py`

2. **Integration Tests**

   - Test interaction between components
   - Use real dependencies where possible
   - Focus on data flow and state management
   - Example: `test_agent_criteria_manager.py`

3. **Acceptance Tests**
   - End-to-end tests of the agent
   - Test complete workflows
   - Verify agent behavior matches requirements
   - Example: `test_todo_implementation.py`

## Writing Tests

### Test Structure

- Group related tests in classes
- Use descriptive test names that explain the scenario
- Include detailed docstrings explaining requirements and assumptions
- See `docs/test_template.py` for examples

### Fixtures

- Use fixtures for common setup/teardown
- Keep fixtures focused and composable
- Document fixture dependencies and return values
- Place shared fixtures in `tests/utils/fixtures.py`

### Test Data

- Use clear, minimal test data that illustrates the scenario
- Document data assumptions and requirements
- Store large test data in separate files under `tests/data/`

## Testing the Agent

### Key Areas to Test

1. **Tool Usage**

   - Correct tool selection
   - Proper parameter handling
   - Error handling for tool failures

2. **Code Analysis**

   - Parsing and understanding code
   - Identifying relevant code sections
   - Handling different file types

3. **Code Generation**

   - Code quality and style
   - Error handling
   - Integration with existing code

4. **Test Generation**
   - Test structure and organization
   - Coverage of requirements
   - Handling of edge cases

### Mocking Considerations

- Mock external API calls
- Mock file system operations where appropriate
- Mock time-dependent operations
- Document what is mocked and why

## Test Maintenance

### When Tests Fail

1. Check if it's a legitimate failure or test issue
2. Look for patterns in related test failures
3. Check recent changes that might affect the test
4. Update tests when requirements change

### Updating Tests

- Keep test documentation up to date
- Remove obsolete tests
- Update mocks when dependencies change
- Maintain test data files
