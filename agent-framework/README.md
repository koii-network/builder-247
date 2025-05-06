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

## Testing

### Running Tests

To run tests with coverage:

```bash
# Navigate to the agent-framework directory
cd agent-framework

# Run tests with coverage
./run_tests.sh
```

This will:
- Install dependencies
- Run pytest
- Generate a terminal coverage report
- Create an HTML coverage report in `coverage_report/`

## Documentation

For detailed documentation, please visit [documentation link].

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.