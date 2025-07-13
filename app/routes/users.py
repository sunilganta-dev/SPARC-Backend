from flask import Blueprint, jsonify, request
from app.models.user import User
from app.models.religion import ReligiousProfile
from app.models.background import BackgroundPreferences
from app.models.lifestyle import LifestylePreferences
from app.models.matchmaker import Matchmaker, Applicant
from app import db
from functools import wraps
import jwt
from app import app
from datetime import datetime

users_bp = Blueprint('users', __name__)

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

@users_bp.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    """Create a new user from form data"""
    data = request.json
    
    # Check if user exists by email
    if User.query.filter_by(email=data.get('About You', {}).get('Email')).first():
        return jsonify({'message': 'User with this email already exists'}), 409
    
    try:
        # Create user
        user = User(
            name=data.get('About You', {}).get('Full Name'),
            email=data.get('About You', {}).get('Email'),
            phone=data.get('About You', {}).get('Phone'),
            gender=data.get('About You', {}).get('Gender'),
            dob=parse_date(data.get('About You', {}).get('Date of Birth')),
            hometown=data.get('About You', {}).get('Hometown (where you were raised)'),
            current_location=data.get('About You', {}).get('Current Location'),
            height=data.get('About You', {}).get('Height (ft/in) (ex: 5\'8")'),
            occupation=data.get('About You', {}).get('Occupation (Company & Title)'),
            education_level=data.get('About You', {}).get('Highest level of education completed'),
            schools=data.get('About You', {}).get('Schools Attended (if applicable)')
        )
        db.session.add(user)
        db.session.flush()  # Get user ID without committing
        
        # Create religious profile
        religion_data = data.get('Culture & Religion', {})
        religious_profile = ReligiousProfile(
            user_id=user.id,
            cultural_background=religion_data.get('Cultural Background'),
            languages=religion_data.get('Select the languages you speak'),
            shabbat_observance=religion_data.get('Shabbat Observance'),
            kosher_observance=religion_data.get('Kosher Observance'),
            jewish_learning=religion_data.get('Personal Jewish Learning/Education'),
            synagogue_attendance=religion_data.get('Synagogue Attendance'),
            childrens_education=religion_data.get('Your children\'s Jewish education'),
            shomer_negiah=religion_data.get('Your observance of shomer negiah'),
            male_partner_preference=religion_data.get('For Men: Please answer based on your current perspective for what you are seeking in a spouse'),
            prayer_habits=religion_data.get('Prayer Habits'),
            religious_growth=religion_data.get('Perspective on religious growth')
        )
        db.session.add(religious_profile)
        
        # Create background preferences
        bg_data = data.get('Background & Future', {})
        background = BackgroundPreferences(
            user_id=user.id,
            convert_status=bg_data.get('Conversion History'),
            marital_status=bg_data.get('Marital Status'),
            children=bg_data.get('Children'),
            aliyah=bg_data.get('Aliyah'),
            partner_background=bg_data.get('Ideal Partner\'s Cultural Background'),
            min_partner_height=bg_data.get('Minimum partner height (ft\'in) (ex: 5\'8")'),
            max_partner_age=bg_data.get('Maximum partner age'),
            photo_url=bg_data.get('Upload Photos')
        )
        db.session.add(background)
        
        # Create lifestyle preferences
        lifestyle_data = data.get('Lifestyle & Preferences', {})
        lifestyle = LifestylePreferences(
            user_id=user.id,
            ranked_activities=lifestyle_data.get('Rank these activities in order of how you would spend your free time'),
            living_environment=lifestyle_data.get('Preferred Living Environment'),
            conflict_style=lifestyle_data.get('Conflict Communication Style'),
            life_focus=lifestyle_data.get('Personal Life Focus/Goal'),
            activity_level=lifestyle_data.get('How active are you'),
            alcohol=lifestyle_data.get('Alcohol Habits'),
            smoking=lifestyle_data.get('Smoking Habits'),
            relationship_traits=lifestyle_data.get('Which two traits do you feel are most important in having and maintaining a healthy and successful relationship'),
            ranked_priorities=lifestyle_data.get('Rank these in order of importance/priority')
        )
        db.session.add(lifestyle)
        
        # Link user to matchmaker
        applicant = Applicant(
            user_id=user.id,
            shidduch_lady_id=current_user.id
        )
        db.session.add(applicant)
        
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user_id': user.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating user: {str(e)}'}), 500

@users_bp.route('/user/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """Get user profile details"""
    # Check if user belongs to this matchmaker
    applicant = Applicant.query.filter_by(
        user_id=user_id,
        shidduch_lady_id=current_user.id
    ).first()
    
    # Allow admin to see all users
    is_admin = current_user.email == app.config.get('ADMIN_EMAIL')
    
    if not (applicant or is_admin):
        return jsonify({'message': 'User not found or not authorized'}), 404
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'gender': user.gender,
            'dob': format_date(user.dob),
            'age': calculate_age(user.dob),
            'hometown': user.hometown,
            'current_location': user.current_location,
            'height': user.height,
            'occupation': user.occupation,
            'education_level': user.education_level,
            'schools': user.schools
        },
        'religious_profile': get_religious_profile(user),
        'background': get_background(user),
        'lifestyle': get_lifestyle(user)
    })

@users_bp.route('/matchmaker/users', methods=['GET'])
@token_required
def get_matchmaker_users(current_user):
    """Get all users belonging to a matchmaker"""
    applicants = Applicant.query.filter_by(shidduch_lady_id=current_user.id).all()
    user_ids = [a.user_id for a in applicants]
    
    users = User.query.filter(User.id.in_(user_ids)).all()
    
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'gender': user.gender,
            'age': calculate_age(user.dob),
            'current_location': user.current_location
        })

    # print(user_list)
    
    return jsonify({
        'users': user_list,
        'count': len(user_list)
    })

# Helper functions
def parse_date(date_str):
    """Parse date string to Python date object"""
    if not date_str:
        return None
    
    try:
        # Try various formats
        for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        # If all formats fail, return None
        return None
    except:
        return None

def format_date(date_obj):
    """Format date object to string"""
    if not date_obj:
        return None
    return date_obj.strftime('%Y-%m-%d')

def calculate_age(dob):
    """Calculate age from date of birth"""
    if not dob:
        return None
    
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def get_religious_profile(user):
    """Get religious profile data for a user"""
    profile = ReligiousProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return {}
    
    return {
        'cultural_background': profile.cultural_background,
        'languages': profile.languages,
        'shabbat_observance': profile.shabbat_observance,
        'kosher_observance': profile.kosher_observance,
        'jewish_learning': profile.jewish_learning,
        'synagogue_attendance': profile.synagogue_attendance,
        'childrens_education': profile.childrens_education,
        'shomer_negiah': profile.shomer_negiah,
        'male_partner_preference': profile.male_partner_preference,
        'prayer_habits': profile.prayer_habits,
        'religious_growth': profile.religious_growth
    }

def get_background(user):
    """Get background preferences data for a user"""
    bg = BackgroundPreferences.query.filter_by(user_id=user.id).first()
    if not bg:
        return {}
    
    return {
        'convert_status': bg.convert_status,
        'marital_status': bg.marital_status,
        'children': bg.children,
        'aliyah': bg.aliyah,
        'partner_background': bg.partner_background,
        'min_partner_height': bg.min_partner_height,
        'max_partner_age': bg.max_partner_age,
        'photo_url': bg.photo_url
    }

def get_lifestyle(user):
    """Get lifestyle preferences data for a user"""
    ls = LifestylePreferences.query.filter_by(user_id=user.id).first()
    if not ls:
        return {}
    
    return {
        'ranked_activities': ls.ranked_activities,
        'living_environment': ls.living_environment,
        'conflict_style': ls.conflict_style,
        'life_focus': ls.life_focus,
        'activity_level': ls.activity_level,
        'alcohol': ls.alcohol,
        'smoking': ls.smoking,
        'relationship_traits': ls.relationship_traits,
        'ranked_priorities': ls.ranked_priorities
    }
