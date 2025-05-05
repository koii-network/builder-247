"""
Test suite for the Security Consultation module.
"""

import pytest
from src.security_consultation import create_security_consultation, SecurityConsultation

def test_create_security_consultation():
    """Test creating a security consultation instance."""
    consultation = create_security_consultation("Test System")
    assert isinstance(consultation, SecurityConsultation)
    assert consultation.system_name == "Test System"

def test_add_risk():
    """Test adding a security risk."""
    consultation = create_security_consultation("Test System")
    consultation.add_risk("Data Exposure", "High", "Sensitive data may be exposed")
    
    assert len(consultation.risks) == 1
    assert consultation.risks[0]['type'] == "Data Exposure"
    assert consultation.risks[0]['severity'] == "High"

def test_invalid_risk_severity():
    """Test that an invalid severity raises a ValueError."""
    consultation = create_security_consultation("Test System")
    with pytest.raises(ValueError):
        consultation.add_risk("Test Risk", "Invalid", "Description")

def test_add_recommendation():
    """Test adding a security recommendation."""
    consultation = create_security_consultation("Test System")
    consultation.add_recommendation("Implement multi-factor authentication")
    
    assert len(consultation.recommendations) == 1
    assert consultation.recommendations[0] == "Implement multi-factor authentication"

def test_generate_report():
    """Test generating a security consultation report."""
    consultation = create_security_consultation("Test System")
    consultation.add_risk("Data Exposure", "High", "Sensitive data may be exposed")
    consultation.add_recommendation("Implement encryption")
    
    report = consultation.generate_report()
    
    assert report['system_name'] == "Test System"
    assert report['total_risks'] == 1
    assert len(report['recommendations']) == 1

def test_validate_report():
    """Test report validation."""
    consultation = create_security_consultation("Test System")
    
    # Initially invalid
    assert not consultation.validate_report()
    
    # Add a risk and recommendation
    consultation.add_risk("Test Risk", "Medium", "Test description")
    consultation.add_recommendation("Test recommendation")
    
    # Now valid
    assert consultation.validate_report()