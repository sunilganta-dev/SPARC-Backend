"""
Test the matching algorithm with the generated test data.
This script runs various matching scenarios with the test users.

Usage:
    python test_matching.py

Make sure to run populate_test_data.py first to create test data.
"""

import sys
import os
import random
from tabulate import tabulate

# Add the application root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, app
from app.models.user import User
from app.models.matchmaker import Matchmaker, Applicant
from app.services.match_engine import (
    get_matches_for_user,
    get_all_top_matches,
    get_matchmaker_matches,
    score_match
)

# Configuration
TEST_EMAIL_PREFIX = "test_"
DISPLAY_LIMIT = 10  # Number of matches to display

def find_test_users():
    """Get all test users from the database"""
    return User.query.filter(User.email.like(f"{TEST_EMAIL_PREFIX}%")).all()

def find_test_matchmakers():
    """Get all test matchmakers from the database"""
    return Matchmaker.query.filter(Matchmaker.email.like(f"{TEST_EMAIL_PREFIX}%")).all()

def test_match_specific_user():
    """Test matching for a specific user"""
    test_users = find_test_users()
    
    if not test_users:
        print("No test users found. Please run populate_test_data.py first.")
        return
    
    # Randomly select a user for matching
    user = random.choice(test_users)
    
    print(f"\n=== Testing Matches for User: {user.name} ({user.gender}) ===")
    print(f"Age: {calculate_age(user.dob)} | Location: {user.current_location}")
    
    matches = get_matches_for_user(user.id)
    
    if not matches:
        print("No matches found for this user.")
        return
    
    # Prepare data for display
    table_data = []
    for match in matches[:DISPLAY_LIMIT]:
        match_user = User.query.get(match["user_id"])
        
        # Religious compatibility details
        religious_compat = match.get("compatibility", {}).get("religious_compatibility", {})
        religious_score = religious_compat.get("score", "N/A")
        
        # Family compatibility details
        family_compat = match.get("compatibility", {}).get("family_compatibility", {})
        family_score = family_compat.get("score", "N/A")
        
        table_data.append([
            match["name"],
            match["score"],
            calculate_age(match_user.dob),
            match_user.current_location,
            religious_score,
            family_score
        ])
    
    # Display matches
    headers = ["Name", "Overall Score", "Age", "Location", "Religious Compat", "Family Compat"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Show details for top match
    if matches:
        top_match = matches[0]
        top_match_user = User.query.get(top_match["user_id"])
        print(f"\n=== Detailed Compatibility with Top Match: {top_match_user.name} ===")
        
        compatibility = top_match.get("compatibility", {})
        for category, details in compatibility.items():
            print(f"\n{category.replace('_', ' ').title()}: {details.get('score')}%")
            if 'details' in details:
                for key, value in details['details'].items():
                    print(f"  - {key.title()}: {value}")

def test_all_top_matches():
    """Test finding top matches across all users"""
    print("\n=== Top Matches Across All Users ===")
    
    matches = get_all_top_matches(limit_per_match=5, min_score=70)
    
    if not matches:
        print("No high scoring matches found.")
        return
    
    # Prepare data for display
    table_data = []
    for match in matches[:DISPLAY_LIMIT]:
        table_data.append([
            match["user_a_name"],
            match["user_b_name"],
            match["score"]
        ])
    
    # Display matches
    headers = ["Person A", "Person B", "Compatibility Score"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print(f"\nFound {len(matches)} matches with score >= 70")

def test_matchmaker_matches():
    """Test finding matches for a matchmaker's applicants"""
    matchmakers = find_test_matchmakers()
    
    if not matchmakers:
        print("No test matchmakers found. Please run populate_test_data.py first.")
        return
    
    # Randomly select a matchmaker
    matchmaker = random.choice(matchmakers)
    
    print(f"\n=== Matches for Matchmaker: {matchmaker.name} ===")
    
    matches = get_matchmaker_matches(matchmaker.id)
    
    if not matches:
        print("No matches found for this matchmaker's applicants.")
        return
    
    # Prepare data for display
    table_data = []
    for match in matches[:DISPLAY_LIMIT]:
        table_data.append([
            match["applicant_name"],
            match["match_name"],
            match["score"]
        ])
    
    # Display matches
    headers = ["Applicant", "Potential Match", "Score"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print(f"\nFound {len(matches)} total matches for {matchmaker.name}'s applicants")

def calculate_age(dob):
    """Helper function to calculate age from date of birth"""
    if not dob:
        return "Unknown"
    
    from datetime import datetime
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def main():
    """Run the matching tests"""
    with app.app_context():
        print("Starting matching tests...")
        
        # Test 1: Match for a specific user
        test_match_specific_user()
        
        # Test 2: Find top matches across all users
        test_all_top_matches()
        
        # Test 3: Find matches for a matchmaker's applicants
        test_matchmaker_matches()
        
        print("\nMatching tests complete!")

if __name__ == "__main__":
    main() 