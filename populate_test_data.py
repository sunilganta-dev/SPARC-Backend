"""
Populate the database with test data for the shidduch matching application.
This script creates test matchmakers, users, and all associated profile data.

Usage:
    python populate_test_data.py

All test data will be marked with a test_ prefix in the email addresses
for easy identification and removal.
"""

import sys
import os
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add the application root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, app
from app.models.user import User
from app.models.religion import ReligiousProfile
from app.models.background import BackgroundPreferences
from app.models.lifestyle import LifestylePreferences
from app.models.matchmaker import Matchmaker, Applicant

# Test data constants
TEST_EMAIL_PREFIX = "test_"
NUM_MATCHMAKERS = 3
NUM_USERS_PER_MATCHMAKER = 10  # Total users will be NUM_MATCHMAKERS * NUM_USERS_PER_MATCHMAKER
MALE_RATIO = 0.5  # Ratio of male users vs female

# Sample data lists
first_names_male = ["David", "Jacob", "Samuel", "Benjamin", "Aaron", "Isaac", "Eli", "Jonah", "Ari", 
                    "Moshe", "Daniel", "Joseph", "Ezra", "Nathan", "Adam", "Joshua", "Noah", "Gabriel", 
                    "Simon", "Levi"]
first_names_female = ["Sarah", "Rebecca", "Rachel", "Leah", "Hannah", "Esther", "Abigail", "Miriam", 
                     "Ruth", "Naomi", "Deborah", "Tamar", "Eve", "Rachel", "Adina", "Eliana", "Maya", 
                     "Chava", "Shira", "Talia"]
last_names = ["Cohen", "Levy", "Goldberg", "Friedman", "Katz", "Schwartz", "Abrams", "Rothstein", 
             "Greenberg", "Rosenblum", "Bernstein", "Silverman", "Goldman", "Weiss", "Stern", 
             "Klein", "Shapiro", "Weinstein", "Rosenberg", "Kaplan"]
locations = ["New York, NY", "Los Angeles, CA", "Chicago, IL", "Miami, FL", "Boston, MA", 
            "Atlanta, GA", "Baltimore, MD", "Philadelphia, PA", "Cleveland, OH", "Detroit, MI", 
            "Toronto, Canada", "Montreal, Canada", "Jerusalem, Israel", "Tel Aviv, Israel", 
            "London, UK", "Manchester, UK", "Melbourne, Australia", "Sydney, Australia"]
occupations = ["Software Engineer", "Doctor", "Lawyer", "Teacher", "Accountant", "Investment Banker", 
              "Marketing Manager", "Social Worker", "Psychologist", "Graphic Designer", "Rabbi", 
              "Nurse", "Data Scientist", "Business Analyst", "Sales Representative", "Consultant", 
              "Engineer", "Dentist", "Financial Advisor", "Pharmacist"]
schools = ["Yeshiva University", "Stern College", "Touro College", "Queens College", "NYU", "Columbia University", 
          "Brandeis University", "Harvard University", "University of Pennsylvania", "Rutgers University", 
          "Bar Ilan University", "Hebrew University", "Yeshiva College", "Barnard College", "Binghamton University", 
          "Brooklyn College", "University of Maryland", "Princeton University", "Yale University", "Cornell University"]
education_levels = ["High School or Equivalent", "Associates Degree", "Bachelors Degree", "Masters", "PHD", "Other"]
cultural_backgrounds = ["Ashkenazi", "Ashkenazi - Mix", "Sephardic - Persian", "Sephardic - Syrian, Lebanese, Egyptian", 
                       "Sephardic - Moroccan, Algerian, Tunisian (French)", "Sephardic - Moroccan, Algerian, Tunisian (Israeli)", 
                       "Sephardic - Bukharin", "Sephardic - Israeli Mix", "Other"]
languages = ["Arabic", "English", "French", "Hebrew", "Persian", "Russian", "Spanish", "Other"]
shabbat_observance = ["Shomer Shabbat - Fully Observant", 
                      "Traditional - Lightly Observant. Celebrates/Observes every week, but flexible with electricity", 
                      "Traditional - Celebrates/Observes weekly, but drives and cooks", 
                      "Spiritual - Occasionally has Friday/Shabbat Dinner night dinner", 
                      "Do not observe or celebrate"]
kosher_observance = ["Strictly Kosher", "Kosher Home: eat out Vegan/Sushi", 
                    "Kosher Home: eat out Dairy", "Kosher Home: eat out everything", "Don't Keep Kosher"]
jewish_learning = ["Daily", "Multiple times a week", "Weekly", "Occasionally", "Rarely/Never"]
synagogue_attendance = ["Daily", "Weekly", "Occasionally", "Major holidays only", "Rarely/Never"]
childrens_education = ["Essential and non-negotiable", "Important but can be provided outside of school", 
                      "Valuable but not essential", "Open to it, though not a priority", "Not a priority"]
shomer_negiah = ["Am fully shomer negiah", "Am actively working on it", "Am not shomer negiah"]
male_preferences = ["Strictly wears skirts and plans to cover hair", "Wears skirts but does not plan to cover hair", 
                   "Not strict about the laws of tzniut but make an effort", "Generally wear pants but dress conservatively", 
                   "Indifferent to the laws of modesty", "I wear whatever I'm comfortable with"]
prayer_habits = ["Daven with a minyan consistently", "Davens 3x a day individually", 
                "Davens Daily", "Weekly", "Not often"]
religious_growth = ["Looking to grow", "Open to growth", "Open to discussion", "Happy where I am"]
conversion_history = ["I am not a convert", "I am a convert", "I am not a convert, but I have conversion history in my family"]
marital_status = ["Never married", "Previously Engaged", "Divorced", "Widowed"]
children_pref = ["Want Children", "Don't want children", "Have children and want more", "Have children and do not want more"]
aliyah = ["Yes", "No", "Open"]
partner_background = ["Open to all", "Ashkenaz", "Sephardic", "Same as Self"]
free_time_activities = ["Relaxing Activities", "Cultural Activities", "Social Activities", "Outdoor Activities", 
                       "Creative Activities", "Educational Activities", "Physical Activities", "Volunteering Activities"]
living_environment = ["Specific City/Town", "Slightly open to nearby cities/states", 
                     "Open to relocating nationally", "Open to relocating internationally"]
conflict_style = ["Direct and open", "Calm and reflective", "Avoids confrontation", "Prefers mediation"]
life_focus = ["Family/community oriented balance", "Career/family oriented balance", 
              "Family/social oriented balance", "Career Driven", "Self-fulfillment focus", "Travel"]
activity_level = ["Very Active (5-7 times per week)", "Active (3-4 times per week)", 
                 "Somewhat Active (1-2 times per week)", "Not Active"]
substance_habits = ["Regularly", "Socially", "Occasionally/Rarely", "Never"]
relationship_traits = ["Personal space", "Mutual consideration/respect", "Simplicity", "Peacefulness", 
                      "Accepting imperfections", "Trying new things", "Routine", "Communication"]
priorities = ["Family", "Partner Satisfaction", "Self-Satisfaction", "Career", "Religion", "Friends"]

def generate_height():
    """Generate a random height in the format 5'8\" """
    feet = random.randint(4, 6)
    inches = random.randint(0, 11)
    return f"{feet}'{inches}\""

def generate_date_of_birth():
    """Generate a random date of birth for someone between 20 and 40 years old"""
    today = datetime.now()
    age = random.randint(20, 40)
    days_offset = random.randint(0, 365)
    return today - timedelta(days=age*365 + days_offset)

def create_test_matchmakers():
    """Create test matchmaker accounts"""
    matchmakers = []
    for i in range(NUM_MATCHMAKERS):
        matchmaker = Matchmaker(
            name=f"Test Matchmaker {i+1}",
            email=f"{TEST_EMAIL_PREFIX}matchmaker{i+1}@example.com",
            password_hash=generate_password_hash("password123")
        )
        db.session.add(matchmaker)
        matchmakers.append(matchmaker)
    
    db.session.commit()
    print(f"Created {NUM_MATCHMAKERS} test matchmakers")
    return matchmakers

def create_test_users(matchmakers):
    """Create test users with full profiles"""
    total_users = len(matchmakers) * NUM_USERS_PER_MATCHMAKER
    male_count = int(total_users * MALE_RATIO)
    female_count = total_users - male_count
    
    user_count = 0
    
    # Create male users
    for i in range(male_count):
        matchmaker = matchmakers[i % len(matchmakers)]
        first_name = random.choice(first_names_male)
        last_name = random.choice(last_names)
        
        user = User(
            name=f"{first_name} {last_name}",
            email=f"{TEST_EMAIL_PREFIX}{first_name.lower()}.{last_name.lower()}{i}@example.com",
            phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            gender="Male",
            dob=generate_date_of_birth().date(),
            hometown=random.choice(locations),
            current_location=random.choice(locations),
            height=generate_height(),
            occupation=f"{random.choice(occupations)} at {random.choice(['Google', 'Apple', 'Amazon', 'Facebook', 'Microsoft', 'Local Business', 'Hospital', 'University', 'Non-profit', 'Government'])}",
            education_level=random.choice(education_levels),
            schools=", ".join(random.sample(schools, random.randint(1, 3)))
        )
        db.session.add(user)
        db.session.flush()  # To get the user ID
        
        # Create religious profile
        create_religious_profile(user.id, is_male=True)
        
        # Create background preferences
        create_background_preferences(user.id, is_male=True)
        
        # Create lifestyle preferences
        create_lifestyle_preferences(user.id)
        
        # Link to matchmaker
        applicant = Applicant(
            user_id=user.id,
            shidduch_lady_id=matchmaker.id
        )
        db.session.add(applicant)
        
        user_count += 1
        if user_count % 10 == 0:
            print(f"Created {user_count} test users so far...")
    
    # Create female users
    for i in range(female_count):
        matchmaker = matchmakers[i % len(matchmakers)]
        first_name = random.choice(first_names_female)
        last_name = random.choice(last_names)
        
        user = User(
            name=f"{first_name} {last_name}",
            email=f"{TEST_EMAIL_PREFIX}{first_name.lower()}.{last_name.lower()}{i}@example.com",
            phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            gender="Female",
            dob=generate_date_of_birth().date(),
            hometown=random.choice(locations),
            current_location=random.choice(locations),
            height=generate_height(),
            occupation=f"{random.choice(occupations)} at {random.choice(['Google', 'Apple', 'Amazon', 'Facebook', 'Microsoft', 'Local Business', 'Hospital', 'University', 'Non-profit', 'Government'])}",
            education_level=random.choice(education_levels),
            schools=", ".join(random.sample(schools, random.randint(1, 3)))
        )
        db.session.add(user)
        db.session.flush()  # To get the user ID
        
        # Create religious profile
        create_religious_profile(user.id, is_male=False)
        
        # Create background preferences
        create_background_preferences(user.id, is_male=False)
        
        # Create lifestyle preferences
        create_lifestyle_preferences(user.id)
        
        # Link to matchmaker
        applicant = Applicant(
            user_id=user.id,
            shidduch_lady_id=matchmaker.id
        )
        db.session.add(applicant)
        
        user_count += 1
        if user_count % 10 == 0:
            print(f"Created {user_count} test users so far...")
    
    db.session.commit()
    print(f"Created {user_count} test users total ({male_count} male, {female_count} female)")

def create_religious_profile(user_id, is_male):
    """Create a religious profile for a user"""
    # Select random values for each field
    selected_cultural_bg = random.choice(cultural_backgrounds)
    selected_languages = random.sample(languages, random.randint(1, 3))
    selected_shabbat = random.choice(shabbat_observance)
    selected_kosher = random.choice(kosher_observance)
    selected_learning = random.choice(jewish_learning)
    selected_synagogue = random.choice(synagogue_attendance)
    selected_education = random.choice(childrens_education)
    selected_negiah = random.choice(shomer_negiah)
    selected_prayer = random.choice(prayer_habits)
    selected_growth = random.choice(religious_growth)
    
    # For males, include preference for female tzniut
    selected_male_preference = random.choice(male_preferences) if is_male else None
    
    profile = ReligiousProfile(
        user_id=user_id,
        cultural_background=[selected_cultural_bg],
        languages=selected_languages,
        shabbat_observance=selected_shabbat,
        kosher_observance=selected_kosher,
        jewish_learning=selected_learning,
        synagogue_attendance=selected_synagogue,
        childrens_education=selected_education,
        shomer_negiah=selected_negiah,
        male_partner_preference=selected_male_preference,
        prayer_habits=selected_prayer,
        religious_growth=selected_growth
    )
    
    db.session.add(profile)

def create_background_preferences(user_id, is_male):
    """Create background preferences for a user"""
    # Generate random height requirements (only relevant for males seeking females)
    min_height = generate_height() if is_male else None
    max_age = random.randint(25, 45)  # Age range for potential partner
    
    background = BackgroundPreferences(
        user_id=user_id,
        convert_status=random.choice(conversion_history),
        marital_status=random.choice(marital_status),
        children=random.choice(children_pref),
        aliyah=random.choice(aliyah),
        partner_background=random.choice(partner_background),
        min_partner_height=min_height,
        max_partner_age=max_age,
        photo_url=f"https://example.com/photos/test_user_{user_id}.jpg"
    )
    
    db.session.add(background)

def create_lifestyle_preferences(user_id):
    """Create lifestyle preferences for a user"""
    # Generate random ordering of activities
    activities = random.sample(free_time_activities, len(free_time_activities))
    
    # Choose two random relationship traits
    selected_traits = random.sample(relationship_traits, 2)
    
    # Generate random ordering of priorities
    selected_priorities = random.sample(priorities, len(priorities))
    
    lifestyle = LifestylePreferences(
        user_id=user_id,
        ranked_activities=activities,
        living_environment=random.choice(living_environment),
        conflict_style=random.choice(conflict_style),
        life_focus=random.choice(life_focus),
        activity_level=random.choice(activity_level),
        alcohol=random.choice(substance_habits),
        smoking=random.choice(substance_habits),
        relationship_traits=selected_traits,
        ranked_priorities=selected_priorities
    )
    
    db.session.add(lifestyle)

def main():
    """Run the test data population script"""
    with app.app_context():
        print("Starting test data population...")
        
        # Create test matchmakers
        matchmakers = create_test_matchmakers()
        
        # Create test users with their profiles
        create_test_users(matchmakers)
        
        print("Test data population complete!")

if __name__ == "__main__":
    main() 