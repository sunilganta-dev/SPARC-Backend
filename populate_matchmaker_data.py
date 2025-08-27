"""
Script to populate test matchmaker data with realistic information.
"""

import sys
import os

# Add the application root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, app
from app.models.matchmaker import Matchmaker

def populate_test_matchmaker():
    """Create or update a test matchmaker with realistic data"""
    with app.app_context():
        try:
            # Check if a matchmaker already exists
            matchmaker = Matchmaker.query.first()
            
            if not matchmaker:
                # Create a new matchmaker
                matchmaker = Matchmaker(
                    name='Sarah Cohen',
                    email='sarah.cohen@sparcmatchmaking.com',
                    password_hash='hashed_password_here'
                )
                db.session.add(matchmaker)
                print("Created new matchmaker")
            else:
                print(f"Updating existing matchmaker: {matchmaker.name}")
            
            # Update profile information
            matchmaker.organization = 'SPARC Matchmaking Services'
            matchmaker.phone = '+1 (212) 555-7890'
            matchmaker.location = 'Brooklyn, NY'
            matchmaker.experience_years = 8
            matchmaker.bio = ('Dedicated matchmaker with over 8 years of experience in the Orthodox Jewish community. '
                             'Specializing in creating meaningful connections based on shared values, religious observance, '
                             'and personal compatibility. I take pride in understanding each individual\'s unique needs '
                             'and preferences to find their perfect match.')
            matchmaker.website = 'https://www.sparcmatchmaking.com'
            
            # Set specializations
            matchmaker.set_specializations([
                'religious',
                'cultural', 
                'young professionals',
                'modern orthodox',
                'graduate professionals'
            ])
            
            # Set social media
            matchmaker.set_social_media({
                'linkedin': 'https://linkedin.com/in/sarah-cohen-matchmaker',
                'facebook': 'https://facebook.com/sparcmatchmaking',
                'instagram': 'https://instagram.com/sparcmatchmaking',
                'website': 'https://www.sparcmatchmaking.com'
            })
            
            db.session.commit()
            
            print("Matchmaker profile updated successfully!")
            print(f"Name: {matchmaker.name}")
            print(f"Email: {matchmaker.email}")
            print(f"Organization: {matchmaker.organization}")
            print(f"Experience: {matchmaker.experience_years} years")
            print(f"Specializations: {matchmaker.get_specializations()}")
            
            return True
            
        except Exception as e:
            print(f"Error updating matchmaker: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = populate_test_matchmaker()
    if success:
        print("\nTest matchmaker data populated successfully!")
    else:
        print("\nFailed to populate test data!")
