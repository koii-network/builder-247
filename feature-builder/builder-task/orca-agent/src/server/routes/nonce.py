from flask import Blueprint, jsonify, request
from ..utils.nonce import nonce_manager

nonce_bp = Blueprint('nonce', __name__)

@nonce_bp.route('/get_nonce', methods=['GET'])
def get_nonce():
    """
    Generate and return a new nonce for client use.
    
    Returns:
        JSON response with a new nonce
    """
    nonce = nonce_manager.generate_nonce()
    return jsonify({'nonce': nonce}), 200