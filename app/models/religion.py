from app import db

class ReligiousProfile(db.Model):
    __tablename__ = 'religious_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cultural_background = db.Column(db.ARRAY(db.String))
    languages = db.Column(db.ARRAY(db.String))
    shabbat_observance = db.Column(db.String)
    kosher_observance = db.Column(db.String)
    jewish_learning = db.Column(db.String)
    synagogue_attendance = db.Column(db.String)
    childrens_education = db.Column(db.String)
    shomer_negiah = db.Column(db.String)
    male_partner_preference = db.Column(db.String)
    prayer_habits = db.Column(db.String)
    religious_growth = db.Column(db.String)
