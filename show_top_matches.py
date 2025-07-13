"""
Show the top 10 matches in the SPARC database.
This script displays the highest compatibility matches with detailed breakdowns.

Usage:
    python show_top_matches.py

Make sure you have users in the database first (either test data or real data).
"""

import sys
import os
from tabulate import tabulate

# Add the application root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, app
from app.models.user import User
from app.services.match_engine import get_all_top_matches

def calculate_age(dob):
    """Helper function to calculate age from date of birth"""
    if not dob:
        return "Unknown"
    
    from datetime import datetime
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def show_database_stats():
    """Show basic database statistics"""
    total_users = User.query.count()
    male_users = User.query.filter_by(gender='Male').count()
    female_users = User.query.filter_by(gender='Female').count()
    
    print("=" * 60)
    print("📊 SPARC DATABASE STATISTICS")
    print("=" * 60)
    print(f"Total Users: {total_users}")
    print(f"Male Users: {male_users}")
    print(f"Female Users: {female_users}")
    print(f"Potential Match Combinations: {male_users * female_users:,}")
    print()

def show_top_matches(limit=10):
    """Show the top matches in the database with detailed information"""
    
    print("🏆" * 20)
    print(f"  TOP {limit} HIGHEST COMPATIBILITY MATCHES")
    print("🏆" * 20)
    print()
    
    # Get all top matches (no minimum score)
    print("🔍 Analyzing all possible matches...")
    matches = get_all_top_matches(limit_per_match=15, min_score=0)
    
    if not matches:
        print("❌ No matches found in database.")
        print("Make sure you have both male and female users in the database.")
        return
    
    print(f"✅ Found {len(matches)} total potential matches")
    print()
    
    # Get top N matches
    top_matches = matches[:limit]
    
    if not top_matches:
        print("❌ No high-quality matches found.")
        return
    
    # Prepare detailed data for display
    print(f"📋 TOP {len(top_matches)} MATCHES:")
    print("-" * 100)
    
    table_data = []
    for i, match in enumerate(top_matches, 1):
        user_a = User.query.get(match["user_a_id"])
        user_b = User.query.get(match["user_b_id"])
        
        # Get additional details
        age_a = calculate_age(user_a.dob) if user_a.dob else "N/A"
        age_b = calculate_age(user_b.dob) if user_b.dob else "N/A"
        
        # Get compatibility scores
        religious_score = "N/A"
        family_score = "N/A"
        
        compatibility = match.get("compatibility", {})
        if "religious_compatibility" in compatibility:
            religious_score = f"{compatibility['religious_compatibility'].get('score', 'N/A')}%"
        if "family_compatibility" in compatibility:
            family_score = f"{compatibility['family_compatibility'].get('score', 'N/A')}%"
        
        # Format location
        location = user_a.current_location[:25] if user_a.current_location else "N/A"
        
        table_data.append([
            f"#{i}",
            f"{match['user_a_name']}",
            f"{age_a}",
            f"{match['user_b_name']}",
            f"{age_b}",
            f"{match['score']:.1f}%",
            religious_score,
            family_score,
            location
        ])
    
    # Display matches table
    headers = ["Rank", "Person A", "Age", "Person B", "Age", "Overall", "Religious", "Family", "Location"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid", 
                   maxcolwidths=[6, 20, 5, 20, 5, 8, 10, 10, 25]))
    
    print()
    
    # Score distribution
    scores = [match['score'] for match in top_matches]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    print(f"📈 SCORE ANALYSIS:")
    print(f"   • Highest Score: {max_score:.1f}%")
    print(f"   • Lowest Score (in top {limit}): {min_score:.1f}%") 
    print(f"   • Average Score: {avg_score:.1f}%")
    print()
    
    # Show detailed breakdown for top 3
    show_detailed_breakdown(top_matches[:3])

def show_detailed_breakdown(top_matches):
    """Show detailed compatibility breakdown for top matches"""
    
    print("🔍" * 20)
    print("  DETAILED COMPATIBILITY BREAKDOWN")
    print("🔍" * 20)
    print()
    
    for i, match in enumerate(top_matches, 1):
        user_a = User.query.get(match["user_a_id"])
        user_b = User.query.get(match["user_b_id"])
        
        print(f"#{i} MATCH: {user_a.name} ❤️ {user_b.name}")
        print(f"Overall Compatibility: {match['score']:.1f}%")
        print("=" * 50)
        
        # Basic demographics
        age_a = calculate_age(user_a.dob) if user_a.dob else "Unknown"
        age_b = calculate_age(user_b.dob) if user_b.dob else "Unknown"
        
        print(f"👤 {user_a.name}:")
        print(f"   • {user_a.gender}, Age {age_a}")
        print(f"   • {user_a.current_location or 'Location not specified'}")
        print(f"   • {user_a.occupation or 'Occupation not specified'}")
        
        print(f"👤 {user_b.name}:")
        print(f"   • {user_b.gender}, Age {age_b}")
        print(f"   • {user_b.current_location or 'Location not specified'}")
        print(f"   • {user_b.occupation or 'Occupation not specified'}")
        
        # Compatibility scores breakdown
        compatibility = match.get("compatibility", {})
        if compatibility:
            print(f"\n📊 Compatibility Scores:")
            for category, details in compatibility.items():
                score = details.get("score", "N/A")
                category_name = category.replace('_', ' ').title()
                print(f"   • {category_name}: {score}%")
                
                # Show specific comparison details
                if "details" in details:
                    for key, value in details["details"].items():
                        print(f"     └─ {key.title()}: {value}")
        
        # Religious compatibility details
        if hasattr(user_a, 'religious_profile') and hasattr(user_b, 'religious_profile'):
            rel_a = user_a.religious_profile
            rel_b = user_b.religious_profile
            if rel_a and rel_b:
                print(f"\n🕯️  Religious Observance Comparison:")
                if rel_a.shabbat_observance and rel_b.shabbat_observance:
                    print(f"   • Shabbat: {rel_a.shabbat_observance} | {rel_b.shabbat_observance}")
                if rel_a.kosher_observance and rel_b.kosher_observance:
                    print(f"   • Kosher: {rel_a.kosher_observance} | {rel_b.kosher_observance}")
                if rel_a.synagogue_attendance and rel_b.synagogue_attendance:
                    print(f"   • Synagogue: {rel_a.synagogue_attendance} | {rel_b.synagogue_attendance}")
        
        # Background compatibility
        if hasattr(user_a, 'background') and hasattr(user_b, 'background'):
            bg_a = user_a.background
            bg_b = user_b.background
            if bg_a and bg_b:
                print(f"\n👨‍👩‍👧‍👦 Family Goals:")
                if bg_a.children and bg_b.children:
                    print(f"   • Children: {bg_a.children} | {bg_b.children}")
                if bg_a.aliyah and bg_b.aliyah:
                    print(f"   • Aliyah: {bg_a.aliyah} | {bg_b.aliyah}")
        
        print("\n" + "="*50 + "\n")

def main():
    """Main function to run the top matches display"""
    with app.app_context():
        print()
        show_database_stats()
        show_top_matches(limit=10)
        
        print("✨ Analysis complete! ✨")
        print()
        print("💡 Tips:")
        print("   • Scores above 80% indicate very strong compatibility")
        print("   • Religious compatibility is weighted heavily in the algorithm")
        print("   • Consider personal chemistry beyond these scores")
        print()

if __name__ == "__main__":
    main()
