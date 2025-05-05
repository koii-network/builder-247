import os
import pytest

def test_security_docs_file_exists():
    """Verify that the security documentation file exists."""
    assert os.path.exists('src/security_consultation_docs.md'), "Security documentation file not found"

def test_security_docs_content():
    """Test the content of the security documentation."""
    with open('src/security_consultation_docs.md', 'r') as doc_file:
        content = doc_file.read()
        
        # Check for key sections
        required_sections = [
            "Overview",
            "Security Review Process",
            "Threat Modeling",
            "Vulnerability Scanning",
            "Access Control Review",
            "Data Protection Evaluation",
            "Infrastructure Security",
            "Reporting and Remediation",
            "Consultation Engagement Model",
            "Best Practices",
            "Tools and Resources",
            "Disclaimer"
        ]
        
        for section in required_sections:
            assert section in content, f"Section '{section}' is missing from documentation"

def test_documentation_structure():
    """Verify the overall structure of the documentation."""
    with open('src/security_consultation_docs.md', 'r') as doc_file:
        lines = doc_file.readlines()
        
        # Check that file starts with a top-level header
        assert lines[0].startswith('# '), "Documentation should start with a top-level header"
        
        # Verify presence of markdown formatting
        assert any(line.startswith('## ') for line in lines), "No secondary headers found"
        assert any(line.startswith('- ') for line in lines), "No list items found"

def test_content_comprehensiveness():
    """Check that the documentation provides comprehensive guidance."""
    with open('src/security_consultation_docs.md', 'r') as doc_file:
        content = doc_file.read()
        
        # Check for depth of content in key areas
        comprehensive_keywords = [
            "identify", "analyze", "verify", "audit", 
            "assessment", "prioritize", "recommendations"
        ]
        
        for keyword in comprehensive_keywords:
            assert keyword.lower() in content.lower(), f"Comprehensive keyword '{keyword}' missing"

def test_best_practices_section():
    """Validate the best practices section."""
    with open('src/security_consultation_docs.md', 'r') as doc_file:
        content = doc_file.read()
        
        best_practices = [
            "conduct reviews regularly",
            "maintain an updated security baseline",
            "foster a proactive security culture",
            "continuously educate team members"
        ]
        
        for practice in best_practices:
            assert practice.lower() in content.lower(), f"Best practice '{practice}' not found"