"""
Security Consultation and Review Module

This module provides tools and utilities for conducting security consultations
and generating comprehensive security review reports.
"""

import logging
from typing import List, Dict, Any

class SecurityConsultation:
    """
    A class to manage security consultation and review processes.
    """

    def __init__(self, system_name: str):
        """
        Initialize a security consultation for a specific system.

        Args:
            system_name (str): Name of the system being reviewed
        """
        self.system_name = system_name
        self.risks: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []
        self.logger = logging.getLogger(__name__)

    def add_risk(self, risk_type: str, severity: str, description: str) -> None:
        """
        Add a security risk to the consultation report.

        Args:
            risk_type (str): Category of the risk
            severity (str): Risk severity level (Low/Medium/High/Critical)
            description (str): Detailed description of the risk
        """
        if severity not in ['Low', 'Medium', 'High', 'Critical']:
            raise ValueError("Invalid severity level")

        risk = {
            'type': risk_type,
            'severity': severity,
            'description': description
        }
        self.risks.append(risk)
        self.logger.warning(f"Security Risk Identified: {risk}")

    def add_recommendation(self, recommendation: str) -> None:
        """
        Add a security recommendation to the consultation report.

        Args:
            recommendation (str): Security improvement recommendation
        """
        self.recommendations.append(recommendation)
        self.logger.info(f"Recommendation Added: {recommendation}")

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive security consultation report.

        Returns:
            Dict[str, Any]: Detailed security consultation report
        """
        report = {
            'system_name': self.system_name,
            'total_risks': len(self.risks),
            'risks': sorted(self.risks, key=lambda x: 
                {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}[x['severity']], 
                reverse=True),
            'recommendations': self.recommendations
        }
        return report

    def validate_report(self) -> bool:
        """
        Validate the completeness of the security consultation report.

        Returns:
            bool: Whether the report meets minimum requirements
        """
        return len(self.risks) > 0 and len(self.recommendations) > 0

def create_security_consultation(system_name: str) -> SecurityConsultation:
    """
    Factory function to create a new security consultation.

    Args:
        system_name (str): Name of the system being reviewed

    Returns:
        SecurityConsultation: An instance of the SecurityConsultation class
    """
    return SecurityConsultation(system_name)