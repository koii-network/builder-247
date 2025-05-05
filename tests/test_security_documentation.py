import os
import pytest

def test_security_documentation_exists():
    """Test that the security documentation file exists."""
    assert os.path.exists('src/security-consultation-review.md'), "Security documentation file is missing"

def test_documentation_content():
    """Test the content of the security documentation."""
    with open('src/security-consultation-review.md', 'r') as doc_file:
        content = doc_file.read()
        
        # Check for key sections
        required_sections = [
            "Overview",
            "Objectives",
            "Consultation Process",
            "Key Evaluation Criteria",
            "Documentation Standards",
            "Reporting",
            "References",
            "Disclaimer"
        ]
        
        for section in required_sections:
            assert section in content, f"Required section '{section}' is missing"

def test_documentation_structure():
    """Validate the structure and formatting of the documentation."""
    with open('src/security-consultation-review.md', 'r') as doc_file:
        lines = doc_file.readlines()
        
        # Check markdown hierarchy
        headers = [line.strip() for line in lines if line.startswith('#')]
        
        assert len(headers) > 0, "Documentation should have headers"
        assert headers[0].startswith('# '), "Top-level header should start with '# '"
        assert any(header.startswith('## ') for header in headers), "Should have second-level headers"

def test_documentation_length():
    """Ensure the documentation has sufficient depth."""
    with open('src/security-consultation-review.md', 'r') as doc_file:
        content = doc_file.read()
        
        # Check minimum content length
        assert len(content) > 500, "Documentation seems too short"

def test_key_keywords():
    """Check for important security-related keywords."""
    with open('src/security-consultation-review.md', 'r') as doc_file:
        content = doc_file.read().lower()
        
        security_keywords = [
            "vulnerability", 
            "threat", 
            "risk", 
            "security", 
            "assessment", 
            "compliance", 
            "mitigation"
        ]
        
        for keyword in security_keywords:
            assert keyword in content, f"Important keyword '{keyword}' is missing"