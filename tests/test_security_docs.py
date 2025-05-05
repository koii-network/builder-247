import os
import pytest

def test_security_documentation_exists():
    """Test that the security documentation file exists."""
    assert os.path.exists('SECURITY_CONSULTATION.md'), "Security documentation file is missing"

def test_security_documentation_content():
    """Verify that the security documentation contains key sections."""
    with open('SECURITY_CONSULTATION.md', 'r') as doc:
        content = doc.read()
        
    required_sections = [
        "Security Assessment Framework",
        "Security Consultation Principles",
        "Security Review Process",
        "Continuous Security Monitoring",
        "Compliance and Standards",
        "Incident Response",
        "Contact and Escalation"
    ]
    
    for section in required_sections:
        assert section in content, f"Section '{section}' is missing from security documentation"

def test_documentation_length():
    """Ensure the documentation is sufficiently comprehensive."""
    with open('SECURITY_CONSULTATION.md', 'r') as doc:
        content = doc.read()
    
    # Check that documentation is more than a minimal length
    assert len(content) > 1000, "Security documentation seems too short"

def test_markdown_formatting():
    """Basic check for markdown formatting."""
    with open('SECURITY_CONSULTATION.md', 'r') as doc:
        content = doc.read()
    
    # Check for headers
    assert content.count('#') > 5, "Insufficient markdown headers"
    
    # Check for lists
    assert '- ' in content, "Missing markdown lists"

def test_version_history():
    """Verify presence of version history."""
    with open('SECURITY_CONSULTATION.md', 'r') as doc:
        content = doc.read()
    
    assert "Revision History" in content, "Version/revision history is missing"
    assert "Version 1.0" in content, "Initial version not documented"