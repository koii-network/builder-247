## Development Process

1. **Planning Phase**
   - Create todo.md with numbered test cases
   - Each test case should be specific and independently verifiable
   - Tests should build upon each other incrementally

2. **Implementation Cycle**
   - For each todo item:
     a. Implement the required code
     b. Write and run test cases
     c. Review logs and output
     d. Iterate until tests pass
     e. Git commit with reference to todo item
     f. Update todo.md to mark item as complete

3. **Documentation**
   - Each implementation should include:
     - Clear docstrings
     - Usage examples
     - Error handling
     - Type hints

4. **Version Control**
   - Commit messages should follow format: `[TODO-#] Description`
   - Each commit should reference the specific todo item
   - Commits should be atomic and focused
   - Push to remote repository after each commit

5. **Testing**
   - Each feature should have unit tests
   - Integration tests for tool interactions
   - Test both success and failure cases
   - Document test coverage 