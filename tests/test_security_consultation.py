"""
Unit tests for the SecurityConsultation class.
"""

import pytest
from src.security_consultation import SecurityConsultation

def test_initialization():
    """Test that a SecurityConsultation instance is created correctly."""
    consultation = SecurityConsultation()
    assert isinstance(consultation.consultation_data, dict)

def test_set_project_name():
    """Test setting a valid project name."""
    consultation = SecurityConsultation()
    consultation.set_project_name("Test Project")
    assert consultation.consultation_data["project_name"] == "Test Project"

def test_set_project_name_invalid():
    """Test setting an invalid project name raises an error."""
    consultation = SecurityConsultation()
    with pytest.raises(ValueError, match="Project name must be a non-empty string"):
        consultation.set_project_name("")
    with pytest.raises(ValueError, match="Project name must be a non-empty string"):
        consultation.set_project_name("  ")

def test_set_consultation_date():
    """Test setting a valid consultation date."""
    consultation = SecurityConsultation()
    consultation.set_consultation_date("2023-06-15")
    assert consultation.consultation_data["consultation_date"] == "2023-06-15"

def test_set_consultation_date_invalid():
    """Test setting an invalid date raises an error."""
    consultation = SecurityConsultation()
    with pytest.raises(ValueError, match="Date must be in YYYY-MM-DD format"):
        consultation.set_consultation_date("15-06-2023")
    with pytest.raises(ValueError, match="Date must be in YYYY-MM-DD format"):
        consultation.set_consultation_date("invalid-date")

def test_add_security_reviewer():
    """Test adding a security reviewer."""
    consultation = SecurityConsultation()
    consultation.add_security_reviewer("John Doe")
    assert "John Doe" in consultation.consultation_data["security_reviewers"]
    
    # Test preventing duplicate reviewers
    consultation.add_security_reviewer("John Doe")
    assert consultation.consultation_data["security_reviewers"].count("John Doe") == 1

def test_add_security_reviewer_invalid():
    """Test adding an invalid security reviewer."""
    consultation = SecurityConsultation()
    with pytest.raises(ValueError, match="Reviewer name must be a non-empty string"):
        consultation.add_security_reviewer("")
    with pytest.raises(ValueError, match="Reviewer name must be a non-empty string"):
        consultation.add_security_reviewer("  ")

def test_add_key_finding():
    """Test adding a key finding."""
    consultation = SecurityConsultation()
    consultation.add_key_finding("Authentication", "Weak password policies detected")
    assert consultation.consultation_data["key_findings"]["Authentication"] == "Weak password policies detected"

def test_add_key_finding_invalid():
    """Test adding invalid key findings."""
    consultation = SecurityConsultation()
    with pytest.raises(ValueError, match="Category must be a non-empty string"):
        consultation.add_key_finding("", "Finding")
    with pytest.raises(ValueError, match="Finding must be a non-empty string"):
        consultation.add_key_finding("Category", "")

def test_add_recommendation():
    """Test adding a security recommendation."""
    consultation = SecurityConsultation()
    consultation.add_recommendation("Implement two-factor authentication")
    assert "Implement two-factor authentication" in consultation.consultation_data["recommendations"]

def test_add_recommendation_invalid():
    """Test adding an invalid recommendation."""
    consultation = SecurityConsultation()
    with pytest.raises(ValueError, match="Recommendation must be a non-empty string"):
        consultation.add_recommendation("")

def test_set_risk_assessment():
    """Test setting risk assessment details."""
    consultation = SecurityConsultation()
    consultation.set_risk_assessment("overall", "High risk due to multiple vulnerabilities")
    assert consultation.consultation_data["risk_assessment"]["overall"] == "High risk due to multiple vulnerabilities"

def test_set_risk_assessment_invalid():
    """Test setting invalid risk assessment."""
    consultation = SecurityConsultation()
    with pytest.raises(ValueError, match="Risk type must be a non-empty string"):
        consultation.set_risk_assessment("", "Details")
    with pytest.raises(ValueError, match="Risk details must be a non-empty string"):
        consultation.set_risk_assessment("type", "")

def test_get_consultation_report():
    """Test getting the full consultation report."""
    consultation = SecurityConsultation()
    consultation.set_project_name("Test Project")
    consultation.set_consultation_date("2023-06-15")
    consultation.add_security_reviewer("Jane Doe")
    consultation.add_key_finding("Authentication", "Weak policies")
    consultation.add_recommendation("Improve password complexity")
    consultation.set_risk_assessment("overall", "Moderate risk")
    
    report = consultation.get_consultation_report()
    assert report["project_name"] == "Test Project"
    assert report["consultation_date"] == "2023-06-15"

def test_get_consultation_report_missing_fields():
    """Test getting report with missing required fields."""
    consultation = SecurityConsultation()
    with pytest.raises(ValueError, match="Missing required field: project_name"):
        consultation.get_consultation_report()
    
    consultation.set_project_name("Test Project")
    with pytest.raises(ValueError, match="Missing required field: consultation_date"):
        consultation.get_consultation_report()