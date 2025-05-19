"""
Import all models to ensure they're registered with SQLAlchemy
"""

from app.models.user import User
from app.models.religion import ReligiousProfile
from app.models.background import BackgroundPreferences
from app.models.lifestyle import LifestylePreferences
from app.models.matchmaker import Matchmaker, Applicant

# This helps ensure all models are properly loaded and tables are created
__all__ = [
    'User',
    'ReligiousProfile', 
    'BackgroundPreferences',
    'LifestylePreferences',
    'Matchmaker',
    'Applicant'
] 