from flask import Blueprint, jsonify, request
from app.models.user import User
from app.models.matchmaker import Matchmaker, Applicant
from app.services.match_engine import (
    get_matches_for_user, 
    get_all_top_matches,
    get_matchmaker_matches
)
from functools import wraps
import jwt
from app import app

matches_bp = Blueprint('matches', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Matchmaker.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

@matches_bp.route('/user/<int:user_id>/matches', methods=['GET'])
@token_required
def get_user_matches(current_user, user_id):
    """Get matches for a specific user"""
    # Check if the user belongs to this matchmaker
    applicant = Applicant.query.filter_by(
        user_id=user_id, 
        shidduch_lady_id=current_user.id
    ).first()
    
    if not applicant:
        return jsonify({'message': 'User not found or not authorized'}), 404
    
    limit = request.args.get('limit', 10, type=int)
    matches = get_matches_for_user(user_id, limit=limit)
    
    return jsonify({
        'matches': matches,
        'count': len(matches)
    })

@matches_bp.route('/matches/all', methods=['GET'])
@token_required
def get_all_matches(current_user):
    """Get all top matches in the system"""
    # Only system admins can see all matches
    if current_user.email != app.config.get('ADMIN_EMAIL'):
        return jsonify({'message': 'Not authorized'}), 403
    
    limit = request.args.get('limit_per_match', 5, type=int)
    min_score = request.args.get('min_score', 50, type=int)
    
    matches = get_all_top_matches(limit_per_match=limit, min_score=min_score)
    
    return jsonify({
        'matches': matches,
        'count': len(matches)
    })

@matches_bp.route('/matchmaker/matches', methods=['GET'])
@token_required
def get_matches_for_matchmaker(current_user):
    """Get matches for all applicants of a matchmaker"""
    limit = request.args.get('limit', 100, type=int)
    matches = get_matchmaker_matches(current_user.id, limit=limit)
    
    return jsonify({
        'matches': matches,
        'count': len(matches)
    })

@matches_bp.route('/matches/compatibility/<int:user_a_id>/<int:user_b_id>', methods=['GET'])
@token_required
def get_match_compatibility(current_user, user_a_id, user_b_id):
    """Get detailed compatibility between two specific users"""
    # Check if at least one user belongs to this matchmaker
    applicant_a = Applicant.query.filter_by(
        user_id=user_a_id,
        shidduch_lady_id=current_user.id
    ).first()
    
    applicant_b = Applicant.query.filter_by(
        user_id=user_b_id,
        shidduch_lady_id=current_user.id
    ).first()
    
    if not (applicant_a or applicant_b):
        return jsonify({'message': 'Not authorized to view this match'}), 403
    
    user_a = User.query.get(user_a_id)
    user_b = User.query.get(user_b_id)
    
    if not user_a or not user_b:
        return jsonify({'message': 'One or both users not found'}), 404
    
    from app.services.match_engine import score_match, get_compatibility_details
    
    score = score_match(user_a, user_b)
    compatibility = get_compatibility_details(user_a, user_b)
    
    return jsonify({
        'user_a': {
            'id': user_a.id,
            'name': user_a.name
        },
        'user_b': {
            'id': user_b.id,
            'name': user_b.name
        },
        'score': score,
        'compatibility': compatibility
    })
