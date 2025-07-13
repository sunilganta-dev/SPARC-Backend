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

def show_top_10_matches():
    """Show the absolute top 10 matches in the entire database with detailed breakdown"""
    print("\n" + "="*80)
    print("🏆 TOP 10 HIGHEST COMPATIBILITY MATCHES IN DATABASE 🏆")
    print("="*80)
    
    # Get all top matches (no minimum score, get more results)
    matches = get_all_top_matches(limit_per_match=10, min_score=0)
    
    if not matches:
        print("No matches found in database.")
        return
    
    # Get top 10 matches
    top_matches = matches[:10]
    
    # Prepare detailed data for display
    table_data = []
    for i, match in enumerate(top_matches, 1):
        user_a = User.query.get(match["user_a_id"])
        user_b = User.query.get(match["user_b_id"])
        
        # Get additional details
        age_a = calculate_age(user_a.dob) if user_a.dob else "Unknown"
        age_b = calculate_age(user_b.dob) if user_b.dob else "Unknown"
        
        # Get religious compatibility if available
        religious_score = "N/A"
        family_score = "N/A"
        
        compatibility = match.get("compatibility", {})
        if "religious_compatibility" in compatibility:
            religious_score = f"{compatibility['religious_compatibility'].get('score', 'N/A')}%"
        if "family_compatibility" in compatibility:
            family_score = f"{compatibility['family_compatibility'].get('score', 'N/A')}%"
        
        table_data.append([
            f"#{i}",
            f"{match['user_a_name']} ({user_a.gender}, {age_a})",
            f"{match['user_b_name']} ({user_b.gender}, {age_b})",
            f"{match['score']}%",
            religious_score,
            family_score,
            user_a.current_location[:20] if user_a.current_location else "N/A"
        ])
    
    # Display matches
    headers = ["Rank", "Person A", "Person B", "Overall", "Religious", "Family", "Location"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid", maxcolwidths=[5, 25, 25, 8, 10, 10, 20]))
    
    # Show detailed breakdown for top 3 matches
    print("\n" + "="*80)
    print("🔍 DETAILED BREAKDOWN OF TOP 3 MATCHES")
    print("="*80)
    
    for i, match in enumerate(top_matches[:3], 1):
        user_a = User.query.get(match["user_a_id"])
        user_b = User.query.get(match["user_b_id"])
        
        print(f"\n#{i} MATCH: {user_a.name} ↔ {user_b.name} ({match['score']}% compatibility)")
        print("-" * 50)
        
        # Basic info
        print(f"👤 {user_a.name}: {user_a.gender}, Age {calculate_age(user_a.dob)}, {user_a.current_location}")
        print(f"👤 {user_b.name}: {user_b.gender}, Age {calculate_age(user_b.dob)}, {user_b.current_location}")
        
        # Compatibility breakdown
        compatibility = match.get("compatibility", {})
        if compatibility:
            print("\n📊 Compatibility Breakdown:")
            for category, details in compatibility.items():
                score = details.get("score", "N/A")
                print(f"   • {category.replace('_', ' ').title()}: {score}%")
                
                # Show specific details if available
                if "details" in details:
                    for key, value in details["details"].items():
                        print(f"     - {key.title()}: {value}")
        
        # Religious profiles if available
        if hasattr(user_a, 'religious_profile') and hasattr(user_b, 'religious_profile'):
            rel_a = user_a.religious_profile
            rel_b = user_b.religious_profile
            if rel_a and rel_b:
                print(f"\n🕯️  Religious Observance:")
                print(f"   • Shabbat: {rel_a.shabbat_observance} | {rel_b.shabbat_observance}")
                print(f"   • Kosher: {rel_a.kosher_observance} | {rel_b.kosher_observance}")
        
        print()

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
        
        # Test 1: Show top 10 matches in database
        show_top_10_matches()
        
        # Test 2: Match for a specific user
        test_match_specific_user()
        
        # Test 3: Find top matches across all users
        test_all_top_matches()
        
        # Test 4: Find matches for a matchmaker's applicants
        test_matchmaker_matches()
        
        print("\nMatching tests complete!")

if __name__ == "__main__":
    main()