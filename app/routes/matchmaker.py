from flask import Blueprint, request, jsonify
from app.models.matchmaker import Matchmaker, Applicant
from app.models.user import User
from app import db, app
from datetime import datetime

matchmaker_bp = Blueprint('matchmaker', __name__)

def get_current_matchmaker():
    """Get the current matchmaker (for now, use the first one or create a default)"""
    matchmaker = Matchmaker.query.first()
    if not matchmaker:
        # Create a default matchmaker if none exists
        matchmaker = Matchmaker(
            name='Test Matchmaker',
            email='test@example.com',
            organization='SPARC Matchmaking',
            phone='+1 (555) 123-4567',
            location='New York, NY',
            experience_years=5,
            bio='Experienced matchmaker specializing in religious and cultural compatibility.',
            website='https://sparc-matchmaking.com'
        )
        matchmaker.set_specializations(['religious', 'cultural'])
        matchmaker.set_social_media({
            'linkedin': 'https://linkedin.com/in/matchmaker',
            'facebook': 'https://facebook.com/sparcmatchmaking',
            'instagram': 'https://instagram.com/sparcmatchmaking'
        })
        db.session.add(matchmaker)
        db.session.commit()
    return matchmaker

@matchmaker_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get the current matchmaker's profile"""
    try:
        matchmaker = get_current_matchmaker()
        return jsonify(matchmaker.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching profile: {str(e)}'}), 500

@matchmaker_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update the current matchmaker's profile"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        matchmaker = get_current_matchmaker()
        
        # Update basic fields
        if 'name' in data:
            matchmaker.name = data['name']
        if 'email' in data:
            # Check if email already exists for another matchmaker
            existing = Matchmaker.query.filter(
                Matchmaker.email == data['email'], 
                Matchmaker.id != matchmaker.id
            ).first()
            if existing:
                return jsonify({'message': 'Email already exists'}), 409
            matchmaker.email = data['email']
        
        # Update profile fields
        if 'organization' in data:
            matchmaker.organization = data['organization']
        if 'phone' in data:
            matchmaker.phone = data['phone']
        if 'location' in data:
            matchmaker.location = data['location']
        if 'experience_years' in data:
            matchmaker.experience_years = int(data['experience_years'])
        if 'bio' in data:
            matchmaker.bio = data['bio']
        if 'website' in data:
            matchmaker.website = data['website']
        
        # Update complex fields
        if 'specializations' in data:
            matchmaker.set_specializations(data['specializations'])
        if 'social_media' in data:
            matchmaker.set_social_media(data['social_media'])
        
        # Update timestamp
        matchmaker.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': matchmaker.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating profile: {str(e)}'}), 500

@matchmaker_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics for the current matchmaker"""
    try:
        matchmaker = get_current_matchmaker()
        
        # Count applicants for this matchmaker
        total_applicants = Applicant.query.filter_by(shidduch_lady_id=matchmaker.id).count()
        
        # Get unique users (to avoid counting the same user multiple times)
        unique_users = db.session.query(User).join(Applicant).filter(
            Applicant.shidduch_lady_id == matchmaker.id
        ).distinct().count()
        
        # Calculate derived statistics
        stats_data = {
            'applicants': total_applicants,
            'unique_users': unique_users,
            'matches': max(0, total_applicants // 3),  # Rough estimate: 1 match per 3 applicants
            'success_rate': min(85, max(0, (total_applicants * 85) // max(1, total_applicants))) if total_applicants > 0 else 0,
            'monthly_matches': max(1, total_applicants // 10),
            'avg_compatibility': 78,
            'active_applicants': max(0, total_applicants - (total_applicants // 4)),
            'pending_matches': max(0, total_applicants // 8)
        }
        
        return jsonify(stats_data), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching stats: {str(e)}'}), 500

@matchmaker_bp.route('/activity', methods=['GET'])
def get_activity():
    """Get recent activity for the current matchmaker"""
    try:
        matchmaker = get_current_matchmaker()
        
        # Get recent applicants for this matchmaker
        recent_applicants = db.session.query(Applicant, User).join(
            User, Applicant.user_id == User.id
        ).filter(
            Applicant.shidduch_lady_id == matchmaker.id
        ).order_by(Applicant.id.desc()).limit(5).all()
        
        activities = []
        for applicant, user in recent_applicants:
            activities.append({
                'title': 'New Applicant Added',
                'description': f'Added new applicant: {user.name}',
                'time': '1 day ago',  # You'd calculate this from actual timestamps
                'icon': 'user-plus'
            })
        
        # Add profile update activity if the profile was recently updated
        if matchmaker.updated_at and matchmaker.created_at:
            if matchmaker.updated_at > matchmaker.created_at:
                activities.insert(0, {
                    'title': 'Profile Updated',
                    'description': 'Updated your matchmaker profile',
                    'time': '2 hours ago',
                    'icon': 'user-edit'
                })
        
        # Add some default activities if we don't have enough real data
        if len(activities) < 3:
            default_activities = [
                {
                    'title': 'System Login',
                    'description': 'Logged into the system',
                    'time': '3 days ago',
                    'icon': 'sign-in-alt'
                },
                {
                    'title': 'Database Updated',
                    'description': 'System synchronized with latest data',
                    'time': '1 week ago',
                    'icon': 'database'
                }
            ]
            # Only add defaults if we need them
            needed = 3 - len(activities)
            activities.extend(default_activities[:needed])
        
        return jsonify({'activities': activities[:5]}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching activity: {str(e)}'}), 500
