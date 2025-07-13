"""
Import applicants from Microsoft Forms export (SPARC format) into the SPARC database.

This script reads the specific Microsoft Forms export format and creates complete user profiles
in the database, including all related tables (religious, background, lifestyle preferences).

Usage:
    python import_microsoft_forms.py SPARC(1-39).xlsx [--matchmaker-email email@example.com] [--dry-run]

The script is specifically designed for the Microsoft Forms export format with 50 columns.
"""

import sys
import os
import argparse
import pandas as pd
from datetime import datetime
from werkzeug.security import generate_password_hash
import re

# Add the application root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, app
from app.models.user import User
from app.models.religion import ReligiousProfile
from app.models.background import BackgroundPreferences
from app.models.lifestyle import LifestylePreferences
from app.models.matchmaker import Matchmaker, Applicant

# Microsoft Forms column mapping to database fields
FORMS_COLUMN_MAPPING = {
    # User table fields
    'user': {
        'Full Name': 'name',
        'Email2': 'email',
        'Phone': 'phone', 
        'Gender': 'gender',
        'Date of Birth\xa0': 'dob',
        'Hometown (where you were raised)': 'hometown',
        'Current Location': 'current_location',
        'Height (ft\'in) [ex: 5\'8]\xa0': 'height',
        'Occupation (Company & Title)': 'occupation',
        'Highest level of education completed': 'education_level',
        'Schools Attended (if applicable): High School, Year Abroad, University, Masters Program, PHD': 'schools'
    },
    
    # Religious profile fields
    'religious': {
        'Cultural Background': 'cultural_background',
        'Select the languages you speak': 'languages',
        'Shabbat Observance': 'shabbat_observance',
        'Kosher Observance': 'kosher_observance',
        'Personal Jewish Learning/Education': 'jewish_learning',
        'Synagogue Attendance': 'synagogue_attendance',
        'Your children\'s Jewish education': 'childrens_education',
        'Your observance of shomer negiah (if this term is unfamiliar to you, please select "am not shomer negiah")': 'shomer_negiah',
        'For Women: Please answer based on your current perspective regarding yourself\u2028\nFor Men: Please answer based on your current perspective for what you are seeking in a spouse\n': 'male_partner_preference',
        'Prayer Habits': 'prayer_habits',
        'Perspective on religious growth': 'religious_growth'
    },
    
    # Background preferences fields
    'background': {
        'Conversion History': 'convert_status',
        'Marital Status': 'marital_status',
        'Children': 'children',
        'Aliyah': 'aliyah',
        'Ideal Partner\'s Cultural Background\n': 'partner_background',
        'Minimum partner height (ft\'in) [ex: 5\'8]\xa0': 'min_partner_height',
        'Maximum partner age': 'max_partner_age',
        'Please email 3 photos of yourself (ideally one formal photo) to tu.beav.365@outlook.com with "full name - Photos" in the subject line (ex: Jon Silverman - Photos) immediately upon completion of th...': 'photo_url'
    },
    
    # Lifestyle preferences fields
    'lifestyle': {
        'Rank these activities in order of how you would spend your free time': 'ranked_activities',
        'Preferred Living Environment': 'living_environment',
        'Conflict Communication Style': 'conflict_style',
        'Personal Life Focus/Goals': 'life_focus',
        'How active are you': 'activity_level',
        'Alcohol Habits': 'alcohol',
        'Smoking Habits': 'smoking',
        'Which two traits do you feel are most important in having and maintaining a healthy and successful relationship': 'relationship_traits',
        'Rank these in order of importance/priority': 'ranked_priorities'
    }
}

# Mapping for Microsoft Forms values to database values
VALUE_MAPPING = {
    'gender': {
        'Male': 'Male',
        'Female': 'Female'
    },
    'education_level': {
        'High School': 'High School or Equivalent',
        'Associates': 'Associates Degree', 
        'Bachelors': 'Bachelors Degree',
        'Bachelors Degree': 'Bachelors Degree',
        'Masters': 'Masters',
        'Masters Degree': 'Masters',
        'PHD': 'PHD',
        'PhD': 'PHD',
        'Other': 'Other'
    },
    'shabbat_observance': {
        'Shomer Shabbat - Fully Observant': 'Shomer Shabbat - Fully Observant',
        'Traditional - Celebrates/Observes every week, but flexible with electricity': 'Traditional - Lightly Observant. Celebrates/Observes every week, but flexible with electricity',
        'Traditional - Celebrates/Observes weekly, but drives and cooks': 'Traditional - Celebrates/Observes weekly, but drives and cooks',
        'Spiritual - Occasionally has Friday/Shabbat Dinner night dinner': 'Spiritual - Occasionally has Friday/Shabbat Dinner night dinner',
        'Do not observe or celebrate': 'Do not observe or celebrate'
    },
    'kosher_observance': {
        'Strictly Kosher': 'Strictly Kosher',
        'Kosher but eat out dairy': 'Kosher Home: eat out Dairy',
        'Kosher Home: eat out Dairy': 'Kosher Home: eat out Dairy',
        'Kosher but eat out vegan/sushi': 'Kosher Home: eat out Vegan/Sushi',
        'Kosher Home: eat out Vegan/Sushi': 'Kosher Home: eat out Vegan/Sushi',
        'Kosher but eat out everything': 'Kosher Home: eat out everything',
        'Kosher Home: eat out everything': 'Kosher Home: eat out everything',
        'Don\'t Keep Kosher': 'Don\'t Keep Kosher',
        'Do not keep kosher': 'Don\'t Keep Kosher'
    },
    'jewish_learning': {
        'Daily': 'Daily',
        'Multiple times a week': 'Multiple times a week',
        'Weekly': 'Weekly',
        'Occasionally': 'Occasionally',
        'Rarely/Never': 'Rarely/Never'
    },
    'synagogue_attendance': {
        'Daily': 'Daily',
        'Weekly': 'Weekly', 
        'Occasionally': 'Occasionally',
        'Major holidays only': 'Major holidays only',
        'Rarely/Never': 'Rarely/Never'
    },
    'childrens_education': {
        'A must': 'Essential and non-negotiable',
        'Essential and non-negotiable': 'Essential and non-negotiable',
        'Important but can be provided outside of school': 'Important but can be provided outside of school',
        'Valuable but not essential': 'Valuable but not essential',
        'Open to it, though not a priority': 'Open to it, though not a priority',
        'Not a priority': 'Not a priority'
    },
    'shomer_negiah': {
        'Am fully shomer negiah': 'Am fully shomer negiah',
        'Am actively working on it': 'Am actively working on it', 
        'Am not shomer negiah': 'Am not shomer negiah'
    },
    'prayer_habits': {
        'Davens/Prays with a minyan consistently': 'Daven with a minyan consistently',
        'Daven with a minyan consistently': 'Daven with a minyan consistently',
        'Davens 3x a day individually': 'Davens 3x a day individually',
        'Davens Daily': 'Davens Daily',
        'Weekly': 'Weekly',
        'Not often': 'Not often'
    },
    'religious_growth': {
        'Looking to grow': 'Looking to grow',
        'Open to growth': 'Open to growth',
        'Open to discussion': 'Open to discussion',
        'Happy where I am': 'Happy where I am'
    },
    'convert_status': {
        'I am not a convert': 'I am not a convert',
        'I am not a convert of any kind': 'I am not a convert',
        'I am a convert': 'I am a convert',
        'I am not a convert, but I have conversion history in my family': 'I am not a convert, but I have conversion history in my family'
    },
    'marital_status': {
        'Never married': 'Never married',
        'Previously Engaged': 'Previously Engaged',
        'Divorced': 'Divorced',
        'Widowed': 'Widowed'
    },
    'children': {
        'Want Children': 'Want Children',
        'Don\'t want children': 'Don\'t want children',
        'Have children and want more': 'Have children and want more',
        'Have children and do not want more': 'Have children and do not want more'
    },
    'aliyah': {
        'Yes': 'Yes',
        'No': 'No', 
        'Open': 'Open'
    },
    'partner_background': {
        'Open to all': 'Open to all',
        'Ashkenaz': 'Ashkenaz',
        'Sephardic': 'Sephardic',
        'Same as Self': 'Same as Self'
    },
    'living_environment': {
        'Specific City/Town': 'Specific City/Town',
        'Slightly open to nearby cities/states': 'Slightly open to nearby cities/states',
        'Slightly open to nearby cities/ states': 'Slightly open to nearby cities/states',
        'Open to relocating nationally': 'Open to relocating nationally',
        'Open to relocating internationally': 'Open to relocating internationally'
    },
    'conflict_style': {
        'Direct and open': 'Direct and open',
        'Calm and reflective': 'Calm and reflective',
        'Avoids confrontation': 'Avoids confrontation',
        'Prefers mediation': 'Prefers mediation'
    },
    'life_focus': {
        'Family/community oriented balance': 'Family/community oriented balance',
        'Career/family oriented balance': 'Career/family oriented balance',
        'Family/social oriented balance': 'Family/social oriented balance',
        'Career Driven': 'Career Driven',
        'Self-fulfillment focus': 'Self-fulfillment focus',
        'Travel': 'Travel'
    },
    'activity_level': {
        'Very Active (5-7 Times per week)': 'Very Active (5-7 times per week)',
        'Very Active (5-7 times per week)': 'Very Active (5-7 times per week)',
        'Active (3-4 times per week)': 'Active (3-4 times per week)',
        'Somewhat Active (1-2 times per week)': 'Somewhat Active (1-2 times per week)',
        'Not Active': 'Not Active'
    },
    'alcohol': {
        'Regularly': 'Regularly',
        'Socially': 'Socially',
        'Occasionally/Rarely': 'Occasionally/Rarely',
        'Never': 'Never'
    },
    'smoking': {
        'Regularly': 'Regularly',
        'Socially': 'Socially', 
        'Occasionally/Rarely': 'Occasionally/Rarely',
        'Never': 'Never'
    }
}

def clean_and_map_value(field_name, value):
    """Clean and map Microsoft Forms values to database values"""
    if pd.isna(value) or value == '':
        return None
    
    value_str = str(value).strip()
    
    # Handle special cases
    if field_name == 'cultural_background':
        return parse_cultural_background(value_str)
    elif field_name == 'languages':
        return parse_languages(value_str)
    elif field_name == 'male_partner_preference':
        return parse_male_partner_preference(value_str)
    elif field_name == 'ranked_activities':
        return parse_ranked_activities(value_str)
    elif field_name == 'relationship_traits':
        return parse_relationship_traits(value_str)
    elif field_name == 'ranked_priorities':
        return parse_ranked_priorities(value_str)
    elif field_name in VALUE_MAPPING:
        return VALUE_MAPPING[field_name].get(value_str, value_str)
    
    return value_str

def parse_cultural_background(value):
    """Parse cultural background from Microsoft Forms format"""
    if not value:
        return []
    
    # Split by semicolon and clean up
    backgrounds = []
    for bg in value.split(';'):
        bg = bg.strip()
        if bg and bg != '':
            # Map some common variations
            if 'Ashkenazi' in bg and 'Mix' in bg:
                backgrounds.append('Ashkenazi - Mix')
            elif 'Ashkenazi' in bg:
                backgrounds.append('Ashkenazi')
            elif 'Sephardic' in bg and 'Persian' in bg:
                backgrounds.append('Sephardic - Persian')
            elif 'Sephardic' in bg and ('Syrian' in bg or 'Lebanese' in bg or 'Egyptian' in bg):
                backgrounds.append('Sephardic - Syrian, Lebanese, Egyptian')
            elif 'Sephardic' in bg and ('Moroccan' in bg or 'Algerian' in bg or 'Tunisian' in bg):
                if 'French' in bg:
                    backgrounds.append('Sephardic - Moroccan, Algerian, Tunisian (French)')
                elif 'Israeli' in bg:
                    backgrounds.append('Sephardic - Moroccan, Algerian, Tunisian (Israeli)')
                else:
                    backgrounds.append('Sephardic - Moroccan, Algerian, Tunisian (Israeli)')
            elif 'Sephardic' in bg and 'Bukharin' in bg:
                backgrounds.append('Sephardic - Bukharin')
            elif 'Sephardic' in bg and 'Israeli' in bg:
                backgrounds.append('Sephardic - Israeli Mix')
            else:
                backgrounds.append('Other')
    
    return backgrounds if backgrounds else ['Other']

def parse_languages(value):
    """Parse languages from Microsoft Forms format"""
    if not value:
        return []
    
    languages = []
    # Split by semicolon and clean up
    for lang in value.split(';'):
        lang = lang.strip()
        if lang and lang != '':
            # Handle some common variations
            if 'English' in lang:
                languages.append('English')
            elif 'Hebrew' in lang:
                languages.append('Hebrew')
            elif 'Spanish' in lang:
                languages.append('Spanish')
            elif 'Persian' in lang:
                languages.append('Persian')
            elif 'French' in lang:
                languages.append('French')
            elif 'Russian' in lang:
                languages.append('Russian')
            elif 'Arabic' in lang:
                languages.append('Arabic')
            else:
                languages.append('Other')
    
    return languages

def parse_male_partner_preference(value):
    """Parse male partner preference from Microsoft Forms format"""
    if not value:
        return None
    
    value = str(value).lower()
    
    if 'strictly' in value and 'skirts' in value and 'cover hair' in value:
        return 'Strictly wears skirts and plans to cover hair'
    elif 'skirts' in value and 'not' in value and 'cover hair' in value:
        return 'Wears skirts but does not plan to cover hair'
    elif 'not strict' in value and 'tzniut' in value:
        return 'Not strict about the laws of tzniut but make an effort'
    elif 'pants' in value and 'conservative' in value:
        return 'Generally wear pants but dress conservatively'
    elif 'indifferent' in value and 'modesty' in value:
        return 'Indifferent to the laws of modesty'
    elif 'whatever' in value and 'comfortable' in value:
        return 'I wear whatever I\'m comfortable with'
    
    return None

def parse_ranked_activities(value):
    """Parse ranked activities from Microsoft Forms format"""
    if not value:
        return []
    
    activities = []
    activity_map = {
        'outdoor': 'Outdoor Activities',
        'physical': 'Physical Activities', 
        'volunteering': 'Volunteering Activities',
        'social': 'Social Activities',
        'educational': 'Educational Activities',
        'relaxing': 'Relaxing Activities',
        'cultural': 'Cultural Activities',
        'creative': 'Creative Activities'
    }
    
    value_lower = str(value).lower()
    for key, activity in activity_map.items():
        if key in value_lower:
            activities.append(activity)
    
    return activities

def parse_relationship_traits(value):
    """Parse relationship traits from Microsoft Forms format"""
    if not value:
        return []
    
    traits = []
    trait_map = {
        'personal space': 'Personal space',
        'mutual consideration': 'Mutual consideration/respect',
        'respect': 'Mutual consideration/respect',
        'simplicity': 'Simplicity',
        'peacefulness': 'Peacefulness',
        'accepting imperfections': 'Accepting imperfections',
        'trying new things': 'Trying new things',
        'routine': 'Routine',
        'communication': 'Communication'
    }
    
    value_lower = str(value).lower()
    for key, trait in trait_map.items():
        if key in value_lower and trait not in traits:
            traits.append(trait)
    
    return traits[:2]  # Limit to 2 traits as specified

def parse_ranked_priorities(value):
    """Parse ranked priorities from Microsoft Forms format"""
    if not value:
        return []
    
    priorities = []
    priority_map = {
        'religion': 'Religion',
        'family': 'Family',
        'partner': 'Partner Satisfaction',
        'self': 'Self-Satisfaction',
        'career': 'Career',
        'friends': 'Friends'
    }
    
    value_lower = str(value).lower()
    for key, priority in priority_map.items():
        if key in value_lower:
            priorities.append(priority)
    
    return priorities

def parse_date(date_str):
    """Parse date string in various formats"""
    if pd.isna(date_str):
        return None
    
    if isinstance(date_str, datetime):
        return date_str.date()
    
    # Try different date formats
    date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
    
    for fmt in date_formats:
        try:
            return datetime.strptime(str(date_str), fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")

def validate_email(email):
    """Basic email validation"""
    return '@' in email and '.' in email

def find_or_create_matchmaker(email):
    """Find existing matchmaker or create a default one"""
    if email:
        matchmaker = Matchmaker.query.filter_by(email=email).first()
        if matchmaker:
            return matchmaker
        else:
            print(f"Warning: Matchmaker with email {email} not found. Creating new matchmaker.")
            matchmaker = Matchmaker(
                name=f"Matchmaker for {email}",
                email=email,
                password_hash=generate_password_hash("temppassword123")
            )
            db.session.add(matchmaker)
            db.session.flush()
            return matchmaker
    
    # Default matchmaker
    default_matchmaker = Matchmaker.query.filter_by(email="forms_import@example.com").first()
    if not default_matchmaker:
        default_matchmaker = Matchmaker(
            name="Microsoft Forms Import",
            email="forms_import@example.com", 
            password_hash=generate_password_hash("temppassword123")
        )
        db.session.add(default_matchmaker)
        db.session.flush()
    
    return default_matchmaker

def create_user_from_forms_row(row_data, row_num):
    """Create a user and all related profiles from Microsoft Forms row data"""
    errors = []
    
    # Extract and validate user data
    user_data = {}
    for forms_col, db_field in FORMS_COLUMN_MAPPING['user'].items():
        if forms_col in row_data:
            value = row_data[forms_col]
            
            if db_field == 'email':
                if pd.isna(value) or not validate_email(str(value)):
                    errors.append(f"Invalid or missing email")
                    continue
                # Check for duplicate email
                existing_user = User.query.filter_by(email=str(value)).first()
                if existing_user:
                    errors.append(f"User with email {value} already exists")
                    continue
                user_data[db_field] = str(value)
            elif db_field == 'dob':
                try:
                    value = parse_date(value)
                    if value:
                        user_data[db_field] = value
                except ValueError as e:
                    errors.append(f"Invalid date format for Date of Birth: {e}")
                    continue
            elif db_field == 'gender':
                value = clean_and_map_value('gender', value)
                if not value:
                    errors.append("Invalid or missing gender")
                    continue
                user_data[db_field] = value
            elif db_field == 'name':
                if pd.isna(value) or str(value).strip() == '':
                    errors.append("Missing name")
                    continue
                user_data[db_field] = str(value).strip()
            else:
                if not pd.isna(value) and str(value).strip() != '':
                    user_data[db_field] = str(value).strip()
    
    # Check required fields
    required_fields = ['name', 'email', 'gender']
    for field in required_fields:
        if field not in user_data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return None, errors
    
    # Create user
    user = User(**user_data)
    db.session.add(user)
    db.session.flush()  # Get user ID
    
    # Create religious profile
    religious_data = {'user_id': user.id}
    for forms_col, db_field in FORMS_COLUMN_MAPPING['religious'].items():
        if forms_col in row_data:
            value = clean_and_map_value(db_field, row_data[forms_col])
            if value is not None:
                religious_data[db_field] = value
    
    if len(religious_data) > 1:  # More than just user_id
        religious_profile = ReligiousProfile(**religious_data)
        db.session.add(religious_profile)
    
    # Create background preferences
    background_data = {'user_id': user.id}
    for forms_col, db_field in FORMS_COLUMN_MAPPING['background'].items():
        if forms_col in row_data:
            value = row_data[forms_col]
            if db_field == 'max_partner_age':
                try:
                    value = int(value) if not pd.isna(value) and str(value).strip() != '' else None
                except (ValueError, TypeError):
                    print(f"Warning (row {row_num}): Invalid max partner age, skipping")
                    continue
            elif db_field == 'photo_url':
                # For photos, we'll just note that they should email photos
                value = "Photos to be emailed separately" if not pd.isna(value) else None
            else:
                value = clean_and_map_value(db_field, value)
            
            if value is not None:
                background_data[db_field] = value
    
    if len(background_data) > 1:  # More than just user_id
        background_preferences = BackgroundPreferences(**background_data)
        db.session.add(background_preferences)
    
    # Create lifestyle preferences
    lifestyle_data = {'user_id': user.id}
    for forms_col, db_field in FORMS_COLUMN_MAPPING['lifestyle'].items():
        if forms_col in row_data:
            value = clean_and_map_value(db_field, row_data[forms_col])
            if value is not None:
                lifestyle_data[db_field] = value
    
    if len(lifestyle_data) > 1:  # More than just user_id
        lifestyle_preferences = LifestylePreferences(**lifestyle_data)
        db.session.add(lifestyle_preferences)
    
    return user, []

def import_from_microsoft_forms(file_path, matchmaker_email=None, dry_run=False):
    """Import users from Microsoft Forms export"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        print(f"Found {len(df)} rows in Microsoft Forms export")
        
        # Find matchmaker
        matchmaker = find_or_create_matchmaker(matchmaker_email)
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            row_num = index + 2  # Excel row number (accounting for header)
            
            try:
                user, errors = create_user_from_forms_row(row.to_dict(), row_num)
                
                if errors:
                    print(f"Row {row_num} - Errors: {'; '.join(errors)}")
                    error_count += 1
                    continue
                
                if user:
                    # Link to matchmaker
                    applicant = Applicant(
                        user_id=user.id,
                        shidduch_lady_id=matchmaker.id
                    )
                    db.session.add(applicant)
                    
                    if not dry_run:
                        db.session.commit()
                    
                    print(f"Row {row_num} - Successfully imported: {user.name} ({user.email})")
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"Row {row_num} - Unexpected error: {str(e)}")
                error_count += 1
                if not dry_run:
                    db.session.rollback()
        
        if dry_run:
            print(f"\nDRY RUN COMPLETE - No data was actually saved to database")
            db.session.rollback()
        else:
            print(f"\nImport complete!")
        
        print(f"Successfully processed: {success_count}")
        print(f"Errors: {error_count}")
        
    except Exception as e:
        print(f"Error reading Microsoft Forms export: {str(e)}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Import applicants from Microsoft Forms export to SPARC database')
    parser.add_argument('forms_file', nargs='?', default='SPARC(1-39).xlsx', help='Path to Microsoft Forms export file')
    parser.add_argument('--matchmaker-email', '-m', help='Email of the matchmaker to assign users to')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Run without saving to database')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.forms_file):
        print(f"Error: File {args.forms_file} does not exist")
        return
    
    with app.app_context():
        print(f"Starting import from Microsoft Forms export: {args.forms_file}")
        if args.dry_run:
            print("DRY RUN MODE - No data will be saved")
        if args.matchmaker_email:
            print(f"Assigning users to matchmaker: {args.matchmaker_email}")
        
        import_from_microsoft_forms(args.forms_file, args.matchmaker_email, args.dry_run)

if __name__ == "__main__":
    main()
