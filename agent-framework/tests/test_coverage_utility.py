import os
import sys
import subprocess
import pytest
import importlib

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Dynamically import the module
spec = importlib.util.spec_from_file_location(
    "test_coverage", 
    os.path.join(os.path.dirname(__file__), '..', 'prometheus_swarm', 'utils', 'test_coverage.py')
)
test_coverage_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_coverage_module)

def test_run_test_coverage():
    """Test the run_test_coverage function."""
    # Temporarily create a dummy test to ensure coverage runs
    with open('tests/dummy_test.py', 'w') as f:
        f.write("""
def test_dummy():
    assert True
""")
    
    try:
        # Run coverage on dummy test
        result = test_coverage_module.run_test_coverage(['tests/dummy_test.py'])
        assert result == 0, "Test coverage run should succeed"
    finally:
        # Clean up dummy test file
        os.remove('tests/dummy_test.py')

def test_generate_coverage_badge(mocker):
    """Test the generate_coverage_badge function."""
    # Mock subprocess to avoid actual badge generation
    mock_run = mocker.patch('subprocess.run')
    
    test_coverage_module.generate_coverage_badge()
    
    # Verify both coverage XML and badge generation were called
    assert mock_run.call_count == 2
    calls = mock_run.call_args_list
    assert 'coverage' in calls[0][0][0]
    assert 'coverage-badge' in calls[1][0][0]