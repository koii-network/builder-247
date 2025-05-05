"""
Security Consultation and Review Documentation Module

This module provides functionality for generating and managing 
security consultation documentation.
"""

from typing import Dict, List, Optional, Union

class SecurityConsultation:
    """
    A class to manage security consultation and review documentation.
    
    Attributes:
        consultation_data (Dict[str, Union[str, List[str], Dict[str, str]]]): 
            Stores details of the security consultation.
    """
    
    def __init__(self):
        """
        Initialize an empty security consultation document.
        """
        self.consultation_data: Dict[str, Union[str, List[str], Dict[str, str]]] = {
            "project_name": "",
            "consultation_date": "",
            "security_reviewers": [],
            "key_findings": {},
            "recommendations": [],
            "risk_assessment": {},
        }
    
    def set_project_name(self, name: str) -> None:
        """
        Set the name of the project being consulted.
        
        Args:
            name (str): Name of the project.
        
        Raises:
            ValueError: If the name is empty or not a string.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Project name must be a non-empty string")
        self.consultation_data["project_name"] = name.strip()
    
    def set_consultation_date(self, date: str) -> None:
        """
        Set the date of the security consultation.
        
        Args:
            date (str): Date of consultation in a standard format (e.g., YYYY-MM-DD).
        
        Raises:
            ValueError: If the date is invalid.
        """
        # Basic date format validation (can be expanded)
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            raise ValueError("Date must be in YYYY-MM-DD format")
        self.consultation_data["consultation_date"] = date
    
    def add_security_reviewer(self, reviewer: str) -> None:
        """
        Add a security reviewer to the consultation.
        
        Args:
            reviewer (str): Name of the security reviewer.
        
        Raises:
            ValueError: If reviewer name is empty or not a string.
        """
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError("Reviewer name must be a non-empty string")
        
        # Prevent duplicate reviewers
        if reviewer.strip() not in self.consultation_data["security_reviewers"]:
            self.consultation_data["security_reviewers"].append(reviewer.strip())
    
    def add_key_finding(self, category: str, finding: str) -> None:
        """
        Add a key finding to the security consultation.
        
        Args:
            category (str): Category of the finding.
            finding (str): Detailed description of the finding.
        
        Raises:
            ValueError: If category or finding is empty or not a string.
        """
        if not isinstance(category, str) or not category.strip():
            raise ValueError("Category must be a non-empty string")
        
        if not isinstance(finding, str) or not finding.strip():
            raise ValueError("Finding must be a non-empty string")
        
        self.consultation_data["key_findings"][category.strip()] = finding.strip()
    
    def add_recommendation(self, recommendation: str) -> None:
        """
        Add a security recommendation.
        
        Args:
            recommendation (str): Security recommendation.
        
        Raises:
            ValueError: If recommendation is empty or not a string.
        """
        if not isinstance(recommendation, str) or not recommendation.strip():
            raise ValueError("Recommendation must be a non-empty string")
        
        self.consultation_data["recommendations"].append(recommendation.strip())
    
    def set_risk_assessment(self, risk_type: str, details: str) -> None:
        """
        Set risk assessment details for a specific risk type.
        
        Args:
            risk_type (str): Type of risk (e.g., 'overall', 'data_protection').
            details (str): Detailed risk assessment.
        
        Raises:
            ValueError: If risk_type or details is empty or not a string.
        """
        if not isinstance(risk_type, str) or not risk_type.strip():
            raise ValueError("Risk type must be a non-empty string")
        
        if not isinstance(details, str) or not details.strip():
            raise ValueError("Risk details must be a non-empty string")
        
        self.consultation_data["risk_assessment"][risk_type.strip()] = details.strip()
    
    def get_consultation_report(self) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
        """
        Get the complete security consultation report.
        
        Returns:
            Dict containing the full consultation documentation.
        
        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = ["project_name", "consultation_date"]
        for field in required_fields:
            if not self.consultation_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        return self.consultation_data.copy()