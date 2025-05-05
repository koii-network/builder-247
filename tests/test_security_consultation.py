import os
import pytest

def test_security_consultation_docs_exists():
    """Test that the security consultation documentation file exists."""
    assert os.path.exists('src/security_consultation_docs.md'), "Security consultation documentation is missing"

def test_documentation_structure():
    """Test the structure of the security consultation documentation."""
    with open('src/security_consultation_docs.md', 'r') as file:
        content = file.read()
        
        # Check for main sections
        sections = [
            "# Security Consultation and Review Documentation",
            "## Overview",
            "## Security Consultation Process",
            "## Best Practices",
            "## Tools and Technologies",
            "## Incident Response",
            "## Compliance Considerations",
            "## Contact Information"
        ]
        
        for section in sections:
            assert section in content, f"Section {section} is missing from documentation"

def test_detailed_sections():
    """Test that key subsections are present in the documentation."""
    with open('src/security_consultation_docs.md', 'r') as file:
        content = file.read()
        
        subsections = [
            "### 1. Initial Assessment",
            "### 2. Threat Modeling",
            "### 3. Security Review Checklist",
            "#### Infrastructure",
            "#### Application Security",
            "#### Authentication and Authorization",
            "### 4. Vulnerability Assessment",
            "### 5. Reporting"
        ]
        
        for subsection in subsections:
            assert subsection in content, f"Subsection {subsection} is missing from documentation"

def test_contact_information():
    """Test that contact information is present and valid."""
    with open('src/security_consultation_docs.md', 'r') as file:
        content = file.read()
        
        contact_info = [
            "Security Team Email: security@example.com",
            "Incident Reporting: security-incident@example.com"
        ]
        
        for contact in contact_info:
            assert contact in content, f"Contact information {contact} is missing"

def test_checklist_format():
    """Test that checklists use correct markdown checkbox format."""
    with open('src/security_consultation_docs.md', 'r') as file:
        content = file.read()
        checklists = [line for line in content.split('\n') if line.strip().startswith('- [ ]')]
        
        assert len(checklists) > 0, "No checklists found in the documentation"
        for checklist_item in checklists:
            assert checklist_item.startswith('- [ ]'), f"Invalid checklist format: {checklist_item}"