from app import db
from datetime import datetime
import json

class Matchmaker(db.Model):
    __tablename__ = 'shidduch_ladies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    
    # Profile fields
    organization = db.Column(db.String, default='SPARC Matchmaking')
    phone = db.Column(db.String)
    location = db.Column(db.String)
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text)
    website = db.Column(db.String)
    
    # JSON fields for complex data
    specializations = db.Column(db.Text)  # Store as JSON string
    social_media = db.Column(db.Text)    # Store as JSON string
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    applicants = db.relationship('Applicant', backref='matchmaker')
    
    def get_specializations(self):
        """Get specializations as a Python list"""
        if self.specializations:
            try:
                return json.loads(self.specializations)
            except json.JSONDecodeError:
                return []
        return ['religious', 'cultural']  # Default values
    
    def set_specializations(self, specializations_list):
        """Set specializations from a Python list"""
        if isinstance(specializations_list, list):
            self.specializations = json.dumps(specializations_list)
        else:
            self.specializations = json.dumps([])
    
    def get_social_media(self):
        """Get social media as a Python dict"""
        if self.social_media:
            try:
                return json.loads(self.social_media)
            except json.JSONDecodeError:
                return {}
        return {
            'linkedin': '',
            'facebook': '',
            'instagram': ''
        }
    
    def set_social_media(self, social_media_dict):
        """Set social media from a Python dict"""
        if isinstance(social_media_dict, dict):
            self.social_media = json.dumps(social_media_dict)
        else:
            self.social_media = json.dumps({})
    
    def to_dict(self):
        """Convert the matchmaker to a dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'organization': self.organization or 'SPARC Matchmaking',
            'phone': self.phone or '',
            'location': self.location or '',
            'experience_years': self.experience_years or 0,
            'bio': self.bio or 'Experienced matchmaker specializing in religious and cultural compatibility.',
            'website': self.website or '',
            'specializations': self.get_specializations(),
            'social_media': self.get_social_media(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Applicant(db.Model):
    __tablename__ = 'applicants'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    shidduch_lady_id = db.Column(db.Integer, db.ForeignKey('shidduch_ladies.id'))