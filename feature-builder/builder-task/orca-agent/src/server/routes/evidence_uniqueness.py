"""
Server-side route for evidence uniqueness validation.

This module provides server-side validation to ensure the uniqueness of evidence
in the system, preventing duplicate submissions.
"""

from typing import Dict, Any
from flask import request, jsonify
from flask.views import MethodView

class EvidenceUniquenessValidationRoute(MethodView):
    """
    Route class for validating the uniqueness of evidence.
    """

    def __init__(self, database_service):
        """
        Initialize the route with a database service.

        Args:
            database_service: Service for database operations
        """
        self.database_service = database_service

    def post(self) -> Dict[str, Any]:
        """
        Validate the uniqueness of submitted evidence.

        Returns:
            A JSON response indicating the uniqueness status of the evidence.
        """
        try:
            # Get the evidence data from the request
            evidence_data = request.json

            if not evidence_data:
                return jsonify({
                    "status": "error",
                    "message": "No evidence data provided"
                }), 400

            # Extract unique identifiers for validation
            unique_fields = evidence_data.get('unique_fields', [])
            
            if not unique_fields:
                return jsonify({
                    "status": "error", 
                    "message": "No unique fields specified for validation"
                }), 400

            # Perform uniqueness check in the database
            uniqueness_results = self._check_evidence_uniqueness(unique_fields)

            if not uniqueness_results['is_unique']:
                return jsonify({
                    "status": "error",
                    "message": "Evidence is not unique",
                    "duplicate_fields": uniqueness_results['duplicate_fields']
                }), 409

            return jsonify({
                "status": "success",
                "message": "Evidence is unique"
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Uniqueness validation failed: {str(e)}"
            }), 500

    def _check_evidence_uniqueness(self, unique_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the uniqueness of evidence based on specified fields.

        Args:
            unique_fields (dict): Dictionary of fields to check for uniqueness

        Returns:
            Dict containing uniqueness status and any duplicate fields
        """
        duplicate_fields = {}
        
        for field, value in unique_fields.items():
            # Check if the field exists and has a value matching any existing record
            existing_record = self.database_service.find_by_field(field, value)
            
            if existing_record:
                duplicate_fields[field] = value

        return {
            'is_unique': len(duplicate_fields) == 0,
            'duplicate_fields': duplicate_fields
        }

def register_evidence_uniqueness_routes(app, database_service):
    """
    Register evidence uniqueness validation routes.

    Args:
        app: Flask application instance
        database_service: Service for database operations
    """
    evidence_route = EvidenceUniquenessValidationRoute(database_service)
    app.add_url_rule(
        '/validate/evidence-uniqueness', 
        view_func=evidence_route.post, 
        methods=['POST']
    )