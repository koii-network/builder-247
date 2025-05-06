# Prometheus Swarm

A framework for building AI agents with Python.

## Features

- FastAPI-based web framework
- SQLAlchemy for database operations
- Redis and Celery for task queue management
- OpenAI integration
- Authentication and authorization
- Async support
- Comprehensive testing setup

## Installation

```bash
pip install prometheus-swarm
```

## Quick Start

```python
from prometheus_swarm.clients import setup_client
```

## Requirements

- Python 3.8 or higher
- See requirements.txt for full dependency list

## Testing and Coverage

This project uses `pytest` for testing and `pytest-cov` for coverage reporting.

### Running Tests

To run tests with coverage:

```bash
pytest
```

### Coverage Reporting

After running tests, you can view:
- Terminal output of coverage 
- XML report at `coverage.xml`
- HTML report at `htmlcov/index.html`

Test coverage configuration can be found in `.coveragerc`

### Test Paths

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`

## Documentation

For detailed documentation, please visit [documentation link].

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.