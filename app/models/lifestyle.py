from app import db

class LifestylePreferences(db.Model):
    __tablename__ = 'lifestyle_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ranked_activities = db.Column(db.ARRAY(db.String))
    living_environment = db.Column(db.String)
    conflict_style = db.Column(db.String)
    life_focus = db.Column(db.String)
    activity_level = db.Column(db.String)
    alcohol = db.Column(db.String)
    smoking = db.Column(db.String)
    relationship_traits = db.Column(db.ARRAY(db.String))
    ranked_priorities = db.Column(db.ARRAY(db.String))
