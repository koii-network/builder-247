import pytest
from prometheus_swarm.utils.math_utils import safe_divide

def test_safe_divide_normal():
    """Test normal division scenario."""
    assert safe_divide(10, 2) == 5.0

def test_safe_divide_by_zero():
    """Test division by zero scenario."""
    assert safe_divide(10, 0) is None

def test_safe_divide_float():
    """Test division with floating-point numbers."""
    assert safe_divide(10.5, 2.1) == 5.0

def test_safe_divide_error_case():
    """Test division with error scenarios."""
    with pytest.raises(TypeError):
        safe_divide("10", 2)  # Type error