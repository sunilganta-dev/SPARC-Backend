from flask import Blueprint, request, jsonify
from app.models.matchmaker import Matchmaker, Applicant
from app.models.user import User
from app import db, app
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register_matchmaker():
    """Register a new matchmaker"""
    data = request.json
    
    # Check if required fields are present
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if matchmaker already exists
    if Matchmaker.query.filter_by(email=data.get('email')).first():
        return jsonify({'message': 'Matchmaker with this email already exists'}), 409
    
    try:
        # Create new matchmaker
        matchmaker = Matchmaker(
            name=data.get('name'),
            email=data.get('email'),
            password_hash=generate_password_hash(data.get('password'))
        )
        
        db.session.add(matchmaker)
        db.session.commit()
        
        return jsonify({
            'message': 'Matchmaker registered successfully',
            'matchmaker_id': matchmaker.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating matchmaker: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a matchmaker and return JWT token"""
    data = request.json
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    # Find matchmaker by email
    matchmaker = Matchmaker.query.filter_by(email=data.get('email')).first()
    
    if not matchmaker:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    # Check password
    if check_password_hash(matchmaker.password_hash, data.get('password')):
        # Generate token
        token = jwt.encode({
            'id': matchmaker.id,
            'email': matchmaker.email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'matchmaker': {
                'id': matchmaker.id,
                'name': matchmaker.name,
                'email': matchmaker.email
            }
        }), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password_request():
    """Request password reset for a matchmaker"""
    data = request.json
    
    if not data or not data.get('email'):
        return jsonify({'message': 'Email is required'}), 400
    
    matchmaker = Matchmaker.query.filter_by(email=data.get('email')).first()
    
    if not matchmaker:
        # Don't reveal that the user doesn't exist
        return jsonify({'message': 'If account exists, password reset link will be sent'}), 200
    
    # In a real application, you would generate a reset token and send an email
    # For this example, we'll just return a success message
    reset_token = str(uuid.uuid4())
    
    # Here you would save the reset token and expiry to the database
    # Then send an email with the reset link
    
    return jsonify({
        'message': 'Password reset link sent',
        'token': reset_token  # Only for demonstration, don't include in production
    }), 200
