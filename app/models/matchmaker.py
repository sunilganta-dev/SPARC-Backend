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
    
    # Relationship with applicants
    applicants = db.relationship('Applicant', backref='matchmaker')

    def get_specializations(self):
        if self.specializations:
            try:
                return json.loads(self.specializations)
            except json.JSONDecodeError:
                return []
        return ['religious', 'cultural']

    def set_specializations(self, specializations_list):
        if isinstance(specializations_list, list):
            self.specializations = json.dumps(specializations_list)
        else:
            self.specializations = json.dumps([])

    def get_social_media(self):
        if self.social_media:
            try:
                return json.loads(self.social_media)
            except json.JSONDecodeError:
                return {}
        return {'linkedin': '', 'facebook': '', 'instagram': ''}

    def set_social_media(self, social_media_dict):
        if isinstance(social_media_dict, dict):
            self.social_media = json.dumps(social_media_dict)
        else:
            self.social_media = json.dumps({})

    def to_dict(self):
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

    # Personal info
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, unique=True, nullable=True)
    phone = db.Column(db.String, nullable=True)
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=True)
    state = db.Column(db.String, nullable=True)
    country = db.Column(db.String, nullable=True)

    # Religious info
    religious_level = db.Column(db.String, nullable=True)
    kosher_level = db.Column(db.String, nullable=True)
    shabbat_observance = db.Column(db.String, nullable=True)

    # New field for picture
    picture_url = db.Column(db.String, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "dob": self.dob.isoformat() if self.dob else None,
            "gender": self.gender,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "religious_level": self.religious_level,
            "kosher_level": self.kosher_level,
            "shabbat_observance": self.shabbat_observance,
            "picture_url": self.picture_url,  # ✅ added
            "shidduch_lady_id": self.shidduch_lady_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

