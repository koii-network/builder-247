"""Test coverage configuration."""

def test_coverage_configuration():
    """Ensure test coverage configuration is set up correctly."""
    import pytest
    import coverage

    assert hasattr(pytest, 'mark'), "Pytest should be importable"
    assert hasattr(coverage, 'Coverage'), "Coverage library should be importable"

def test_example_function():
    """A sample function to test coverage reporting."""
    def example_function(x):
        """A simple function with different branches."""
        if x > 0:
            return x * 2
        elif x < 0:
            return x * -1
        else:
            return 0

    assert example_function(5) == 10
    assert example_function(-3) == 3
    assert example_function(0) == 0