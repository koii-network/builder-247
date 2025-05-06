def safe_divide(a, b):
    """
    Safely divide two numbers, handling potential errors.
    
    Args:
        a (int/float): Numerator
        b (int/float): Denominator
    
    Returns:
        float/None: Result of division or None if division is impossible
    """
    if b == 0:
        return None
    return a / b