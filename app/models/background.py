from app import db

class BackgroundPreferences(db.Model):
    __tablename__ = 'background_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    convert_status = db.Column(db.String)
    marital_status = db.Column(db.String)
    children = db.Column(db.String)
    aliyah = db.Column(db.String)
    partner_background = db.Column(db.String)
    min_partner_height = db.Column(db.String)
    max_partner_age = db.Column(db.Integer)
    photo_url = db.Column(db.String)