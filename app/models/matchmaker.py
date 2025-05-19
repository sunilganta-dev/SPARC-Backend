from app import db

class Matchmaker(db.Model):
    __tablename__ = 'shidduch_ladies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)
    applicants = db.relationship('Applicant', backref='matchmaker')

class Applicant(db.Model):
    __tablename__ = 'applicants'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    shidduch_lady_id = db.Column(db.Integer, db.ForeignKey('shidduch_ladies.id'))