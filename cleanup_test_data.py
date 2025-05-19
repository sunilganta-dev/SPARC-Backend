"""
Clean up test data from the database for the shidduch matching application.
This script removes all test users, matchmakers, and their associated data.

Usage:
    python cleanup_test_data.py

All test data is identified by the 'test_' prefix in email addresses.
"""

import sys
import os

# Add the application root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, app
from app.models.user import User
from app.models.religion import ReligiousProfile
from app.models.background import BackgroundPreferences
from app.models.lifestyle import LifestylePreferences
from app.models.matchmaker import Matchmaker, Applicant
from sqlalchemy.sql import text

# Test data marker - all test data has this prefix in email
TEST_EMAIL_PREFIX = "test_"

def cleanup_test_users():
    """Remove all test users and their associated profiles"""
    # Find all test users
    test_users = User.query.filter(User.email.like(f"{TEST_EMAIL_PREFIX}%")).all()
    user_ids = [user.id for user in test_users]
    
    if not user_ids:
        print("No test users found to delete.")
        return 0
    
    count = len(user_ids)
    print(f"Found {count} test users to delete.")
    
    # Delete associated data first to avoid foreign key constraint issues
    if user_ids:
        # Delete religious profiles
        religious_profiles = ReligiousProfile.query.filter(ReligiousProfile.user_id.in_(user_ids)).all()
        for profile in religious_profiles:
            db.session.delete(profile)
        print(f"Deleted {len(religious_profiles)} religious profiles.")
        
        # Delete background preferences
        backgrounds = BackgroundPreferences.query.filter(BackgroundPreferences.user_id.in_(user_ids)).all()
        for bg in backgrounds:
            db.session.delete(bg)
        print(f"Deleted {len(backgrounds)} background preference records.")
        
        # Delete lifestyle preferences
        lifestyles = LifestylePreferences.query.filter(LifestylePreferences.user_id.in_(user_ids)).all()
        for ls in lifestyles:
            db.session.delete(ls)
        print(f"Deleted {len(lifestyles)} lifestyle preference records.")
        
        # Delete applicant entries
        applicants = Applicant.query.filter(Applicant.user_id.in_(user_ids)).all()
        for applicant in applicants:
            db.session.delete(applicant)
        print(f"Deleted {len(applicants)} applicant links.")
        
        # Finally delete the users
        for user in test_users:
            db.session.delete(user)
        
        db.session.commit()
        print(f"Successfully deleted {count} test users and their associated data.")
    
    return count

def cleanup_test_matchmakers():
    """Remove all test matchmakers"""
    # Find all test matchmakers
    test_matchmakers = Matchmaker.query.filter(Matchmaker.email.like(f"{TEST_EMAIL_PREFIX}%")).all()
    
    if not test_matchmakers:
        print("No test matchmakers found to delete.")
        return 0
    
    count = len(test_matchmakers)
    print(f"Found {count} test matchmakers to delete.")
    
    # Delete matchmakers
    for matchmaker in test_matchmakers:
        db.session.delete(matchmaker)
    
    db.session.commit()
    print(f"Successfully deleted {count} test matchmakers.")
    
    return count

def cleanup_orphaned_data():
    """Clean up any orphaned data that might be left"""
    # Clean up any orphaned religious profiles
    orphaned = db.session.query(ReligiousProfile).filter(
        ~ReligiousProfile.user_id.in_(db.session.query(User.id))
    ).all()
    
    for item in orphaned:
        db.session.delete(item)
    
    print(f"Deleted {len(orphaned)} orphaned religious profiles.")
    
    # Clean up any orphaned background preferences
    orphaned = db.session.query(BackgroundPreferences).filter(
        ~BackgroundPreferences.user_id.in_(db.session.query(User.id))
    ).all()
    
    for item in orphaned:
        db.session.delete(item)
    
    print(f"Deleted {len(orphaned)} orphaned background preferences.")
    
    # Clean up any orphaned lifestyle preferences
    orphaned = db.session.query(LifestylePreferences).filter(
        ~LifestylePreferences.user_id.in_(db.session.query(User.id))
    ).all()
    
    for item in orphaned:
        db.session.delete(item)
    
    print(f"Deleted {len(orphaned)} orphaned lifestyle preferences.")
    
    # Clean up any orphaned applicant entries
    orphaned = db.session.query(Applicant).filter(
        (~Applicant.user_id.in_(db.session.query(User.id))) |
        (~Applicant.shidduch_lady_id.in_(db.session.query(Matchmaker.id)))
    ).all()
    
    for item in orphaned:
        db.session.delete(item)
    
    print(f"Deleted {len(orphaned)} orphaned applicant entries.")
    
    db.session.commit()

def verify_cleanup():
    """Verify all test data has been removed"""
    # Check for any remaining test users
    remaining_users = User.query.filter(User.email.like(f"{TEST_EMAIL_PREFIX}%")).count()
    remaining_matchmakers = Matchmaker.query.filter(Matchmaker.email.like(f"{TEST_EMAIL_PREFIX}%")).count()
    
    if remaining_users == 0 and remaining_matchmakers == 0:
        print("Verification: All test data has been successfully removed!")
        return True
    else:
        print(f"Verification failed: {remaining_users} test users and {remaining_matchmakers} "
              f"test matchmakers still remain in the database.")
        return False

def main():
    """Run the test data cleanup script"""
    with app.app_context():
        print("Starting test data cleanup...")
        
        # First remove test users and their profiles
        cleanup_test_users()
        
        # Then remove test matchmakers
        cleanup_test_matchmakers()
        
        # Finally clean up any orphaned data
        cleanup_orphaned_data()
        
        # Verify everything is cleaned up
        verify_cleanup()
        
        print("Test data cleanup complete!")

if __name__ == "__main__":
    # Ask for confirmation before proceeding
    confirm = input("This will permanently delete all test data. Are you sure? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    main() 