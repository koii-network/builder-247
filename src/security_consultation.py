"""
Security Consultation and Review Documentation Module

This module provides functionality for managing security consultations
and generating review documentation.
"""

import datetime
from typing import Dict, List, Optional, Union

class SecurityConsultation:
    """
    A class to manage security consultation and review documentation.
    
    This class allows creation, management, and documentation of security consultations,
    tracking key details like findings, recommendations, and severity.
    """
    
    def __init__(self, project_name: str, consultant: str):
        """
        Initialize a security consultation.
        
        Args:
            project_name (str): Name of the project being reviewed
            consultant (str): Name of the security consultant
        """
        self.project_name = project_name
        self.consultant = consultant
        self.created_at = datetime.datetime.now()
        self.findings: List[Dict[str, Union[str, int]]] = []
        self.recommendations: List[str] = []
        self.status: str = "In Progress"
    
    def add_finding(
        self, 
        description: str, 
        severity: int, 
        category: Optional[str] = None
    ) -> None:
        """
        Add a security finding to the consultation.
        
        Args:
            description (str): Detailed description of the security finding
            severity (int): Severity level of the finding (1-5)
            category (Optional[str]): Optional category of the finding
        
        Raises:
            ValueError: If severity is not between 1 and 5
        """
        if not 1 <= severity <= 5:
            raise ValueError("Severity must be between 1 and 5")
        
        finding = {
            "description": description,
            "severity": severity,
            "category": category or "Uncategorized"
        }
        self.findings.append(finding)
    
    def add_recommendation(self, recommendation: str) -> None:
        """
        Add a security recommendation.
        
        Args:
            recommendation (str): A detailed security recommendation
        """
        self.recommendations.append(recommendation)
    
    def complete_consultation(self) -> Dict[str, Union[str, List, datetime.datetime]]:
        """
        Complete the security consultation and generate a review summary.
        
        Returns:
            Dict containing consultation details
        """
        self.status = "Completed"
        return {
            "project_name": self.project_name,
            "consultant": self.consultant,
            "created_at": self.created_at,
            "status": self.status,
            "findings": self.findings,
            "recommendations": self.recommendations
        }
    
    def get_severity_summary(self) -> Dict[str, int]:
        """
        Generate a summary of finding severities.
        
        Returns:
            Dict with count of findings by severity level
        """
        severity_summary = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for finding in self.findings:
            severity_summary[finding['severity']] += 1
        return severity_summary