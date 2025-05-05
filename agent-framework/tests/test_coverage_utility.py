import os
import subprocess
import pytest
from prometheus_swarm.utils.test_coverage import run_test_coverage, generate_coverage_badge

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
        result = run_test_coverage(['tests/dummy_test.py'])
        assert result == 0, "Test coverage run should succeed"
    finally:
        # Clean up dummy test file
        os.remove('tests/dummy_test.py')

def test_generate_coverage_badge(mocker):
    """Test the generate_coverage_badge function."""
    # Mock subprocess to avoid actual badge generation
    mock_run = mocker.patch('subprocess.run')
    
    generate_coverage_badge()
    
    # Verify both coverage XML and badge generation were called
    assert mock_run.call_count == 2
    calls = mock_run.call_args_list
    assert 'coverage' in calls[0][0][0]
    assert 'coverage-badge' in calls[1][0][0]