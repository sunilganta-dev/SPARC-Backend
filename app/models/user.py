from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    phone = db.Column(db.String)
    gender = db.Column(db.String)
    dob = db.Column(db.Date)
    hometown = db.Column(db.String)
    current_location = db.Column(db.String)
    height = db.Column(db.String)
    occupation = db.Column(db.String)
    education_level = db.Column(db.String)
    schools = db.Column(db.String)

    religious_profile = db.relationship('ReligiousProfile', uselist=False, backref='user')
    background = db.relationship('BackgroundPreferences', uselist=False, backref='user')
    lifestyle = db.relationship('LifestylePreferences', uselist=False, backref='user')