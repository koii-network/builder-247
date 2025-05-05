"""
Tests for the Security Consultation Module
"""

import pytest
from datetime import datetime
from src.security_consultation import SecurityConsultation

def test_initialization():
    """Test initialization of SecurityConsultation"""
    consultation = SecurityConsultation("Project X", "Alice Smith")
    
    assert consultation.project_name == "Project X"
    assert consultation.consultant == "Alice Smith"
    assert isinstance(consultation.created_at, datetime)
    assert consultation.status == "In Progress"
    assert consultation.findings == []
    assert consultation.recommendations == []

def test_add_finding():
    """Test adding findings with various severity levels"""
    consultation = SecurityConsultation("Project Y", "Bob Jones")
    
    consultation.add_finding("Weak password policy", 4, "Authentication")
    consultation.add_finding("Outdated library", 3)
    
    assert len(consultation.findings) == 2
    assert consultation.findings[0]['severity'] == 4
    assert consultation.findings[0]['category'] == "Authentication"
    assert consultation.findings[1]['category'] == "Uncategorized"

def test_invalid_severity():
    """Test that invalid severity raises a ValueError"""
    consultation = SecurityConsultation("Project Z", "Charlie Brown")
    
    with pytest.raises(ValueError):
        consultation.add_finding("Critical issue", 6)
    
    with pytest.raises(ValueError):
        consultation.add_finding("Minor issue", 0)

def test_add_recommendation():
    """Test adding recommendations"""
    consultation = SecurityConsultation("Project A", "Dana White")
    
    consultation.add_recommendation("Update all dependencies")
    consultation.add_recommendation("Implement multi-factor authentication")
    
    assert len(consultation.recommendations) == 2
    assert "Update all dependencies" in consultation.recommendations

def test_complete_consultation():
    """Test completing a consultation"""
    consultation = SecurityConsultation("Project B", "Eva Green")
    
    consultation.add_finding("SQL Injection risk", 5, "Injection")
    consultation.add_recommendation("Use parameterized queries")
    
    result = consultation.complete_consultation()
    
    assert result['status'] == "Completed"
    assert len(result['findings']) == 1
    assert len(result['recommendations']) == 1
    assert result['project_name'] == "Project B"

def test_severity_summary():
    """Test generating severity summary"""
    consultation = SecurityConsultation("Project C", "Frank Miller")
    
    consultation.add_finding("High risk issue", 5)
    consultation.add_finding("Medium risk issue", 3)
    consultation.add_finding("Another high risk", 5)
    consultation.add_finding("Low risk issue", 2)
    
    summary = consultation.get_severity_summary()
    
    assert summary == {1: 0, 2: 1, 3: 1, 4: 0, 5: 2}