"""
Import applicants from Excel file into the SPARC database.

This script reads an Excel file with applicant data and creates complete user profiles
in the database, including all related tables (religious, background, lifestyle preferences).

Usage:
    python import_from_excel.py path/to/excel_file.xlsx [--matchmaker-email email@example.com] [--dry-run]

Excel Column Mapping:
    The script expects specific column names in the Excel file. See COLUMN_MAPPING for details.
    
Required columns:
    - Name
    - Email  
    - Gender (Male/Female)
    - Date of Birth (YYYY-MM-DD format)

Optional columns include religious preferences, background info, lifestyle preferences, etc.
"""

import sys
import os
import argparse
import pandas as pd
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the application root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, app
from app.models.user import User
from app.models.religion import ReligiousProfile
from app.models.background import BackgroundPreferences
from app.models.lifestyle import LifestylePreferences
from app.models.matchmaker import Matchmaker, Applicant

# Excel column mapping to database fields
COLUMN_MAPPING = {
    # User table fields
    'user': {
        'Name': 'name',
        'Email': 'email', 
        'Phone': 'phone',
        'Gender': 'gender',
        'Date of Birth': 'dob',
        'Hometown': 'hometown',
        'Current Location': 'current_location',
        'Height': 'height',
        'Occupation': 'occupation',
        'Education Level': 'education_level',
        'Schools': 'schools'
    },
    
    # Religious profile fields
    'religious': {
        'Cultural Background': 'cultural_background',
        'Languages': 'languages',
        'Shabbat Observance': 'shabbat_observance',
        'Kosher Observance': 'kosher_observance',
        'Jewish Learning': 'jewish_learning',
        'Synagogue Attendance': 'synagogue_attendance',
        'Childrens Education': 'childrens_education',
        'Shomer Negiah': 'shomer_negiah',
        'Male Partner Preference': 'male_partner_preference',
        'Prayer Habits': 'prayer_habits',
        'Religious Growth': 'religious_growth'
    },
    
    # Background preferences fields
    'background': {
        'Convert Status': 'convert_status',
        'Marital Status': 'marital_status',
        'Children': 'children',
        'Aliyah': 'aliyah',
        'Partner Background': 'partner_background',
        'Min Partner Height': 'min_partner_height',
        'Max Partner Age': 'max_partner_age',
        'Photo URL': 'photo_url'
    },
    
    # Lifestyle preferences fields
    'lifestyle': {
        'Ranked Activities': 'ranked_activities',
        'Living Environment': 'living_environment',
        'Conflict Style': 'conflict_style',
        'Life Focus': 'life_focus',
        'Activity Level': 'activity_level',
        'Alcohol': 'alcohol',
        'Smoking': 'smoking',
        'Relationship Traits': 'relationship_traits',
        'Ranked Priorities': 'ranked_priorities'
    }
}

# Valid values for dropdown fields (for validation)
VALID_VALUES = {
    'gender': ['Male', 'Female'],
    'education_level': ['High School or Equivalent', 'Associates Degree', 'Bachelors Degree', 'Masters', 'PHD', 'Other'],
    'cultural_background': ['Ashkenazi', 'Ashkenazi - Mix', 'Sephardic - Persian', 'Sephardic - Syrian, Lebanese, Egyptian', 
                           'Sephardic - Moroccan, Algerian, Tunisian (French)', 'Sephardic - Moroccan, Algerian, Tunisian (Israeli)', 
                           'Sephardic - Bukharin', 'Sephardic - Israeli Mix', 'Other'],
    'languages': ['Arabic', 'English', 'French', 'Hebrew', 'Persian', 'Russian', 'Spanish', 'Other'],
    'shabbat_observance': ['Shomer Shabbat - Fully Observant', 
                          'Traditional - Lightly Observant. Celebrates/Observes every week, but flexible with electricity', 
                          'Traditional - Celebrates/Observes weekly, but drives and cooks', 
                          'Spiritual - Occasionally has Friday/Shabbat Dinner night dinner', 
                          'Do not observe or celebrate'],
    'kosher_observance': ['Strictly Kosher', 'Kosher Home: eat out Vegan/Sushi', 
                         'Kosher Home: eat out Dairy', 'Kosher Home: eat out everything', 'Don\'t Keep Kosher'],
    'jewish_learning': ['Daily', 'Multiple times a week', 'Weekly', 'Occasionally', 'Rarely/Never'],
    'synagogue_attendance': ['Daily', 'Weekly', 'Occasionally', 'Major holidays only', 'Rarely/Never'],
    'childrens_education': ['Essential and non-negotiable', 'Important but can be provided outside of school', 
                           'Valuable but not essential', 'Open to it, though not a priority', 'Not a priority'],
    'shomer_negiah': ['Am fully shomer negiah', 'Am actively working on it', 'Am not shomer negiah'],
    'male_partner_preference': ['Strictly wears skirts and plans to cover hair', 'Wears skirts but does not plan to cover hair', 
                               'Not strict about the laws of tzniut but make an effort', 'Generally wear pants but dress conservatively', 
                               'Indifferent to the laws of modesty', 'I wear whatever I\'m comfortable with'],
    'prayer_habits': ['Daven with a minyan consistently', 'Davens 3x a day individually', 
                     'Davens Daily', 'Weekly', 'Not often'],
    'religious_growth': ['Looking to grow', 'Open to growth', 'Open to discussion', 'Happy where I am'],
    'convert_status': ['I am not a convert', 'I am a convert', 'I am not a convert, but I have conversion history in my family'],
    'marital_status': ['Never married', 'Previously Engaged', 'Divorced', 'Widowed'],
    'children': ['Want Children', 'Don\'t want children', 'Have children and want more', 'Have children and do not want more'],
    'aliyah': ['Yes', 'No', 'Open'],
    'partner_background': ['Open to all', 'Ashkenaz', 'Sephardic', 'Same as Self'],
    'living_environment': ['Specific City/Town', 'Slightly open to nearby cities/states', 
                          'Open to relocating nationally', 'Open to relocating internationally'],
    'conflict_style': ['Direct and open', 'Calm and reflective', 'Avoids confrontation', 'Prefers mediation'],
    'life_focus': ['Family/community oriented balance', 'Career/family oriented balance', 
                  'Family/social oriented balance', 'Career Driven', 'Self-fulfillment focus', 'Travel'],
    'activity_level': ['Very Active (5-7 times per week)', 'Active (3-4 times per week)', 
                      'Somewhat Active (1-2 times per week)', 'Not Active'],
    'alcohol': ['Regularly', 'Socially', 'Occasionally/Rarely', 'Never'],
    'smoking': ['Regularly', 'Socially', 'Occasionally/Rarely', 'Never'],
    'ranked_activities': ['Relaxing Activities', 'Cultural Activities', 'Social Activities', 'Outdoor Activities', 
                         'Creative Activities', 'Educational Activities', 'Physical Activities', 'Volunteering Activities'],
    'relationship_traits': ['Personal space', 'Mutual consideration/respect', 'Simplicity', 'Peacefulness', 
                           'Accepting imperfections', 'Trying new things', 'Routine', 'Communication'],
    'ranked_priorities': ['Family', 'Partner Satisfaction', 'Self-Satisfaction', 'Career', 'Religion', 'Friends']
}

def validate_email(email):
    """Basic email validation"""
    return '@' in email and '.' in email

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

def parse_array_field(value):
    """Parse comma-separated values into array"""
    if pd.isna(value) or value == '':
        return []
    
    if isinstance(value, list):
        return value
    
    # Split by comma and clean up
    return [item.strip() for item in str(value).split(',') if item.strip()]

def validate_field_value(field_name, value, row_num):
    """Validate field value against allowed values"""
    if pd.isna(value) or value == '':
        return None
    
    if field_name in VALID_VALUES:
        valid_values = VALID_VALUES[field_name]
        
        # For array fields, validate each item
        if field_name in ['cultural_background', 'languages', 'ranked_activities', 'relationship_traits', 'ranked_priorities']:
            values = parse_array_field(value)
            for val in values:
                if val not in valid_values:
                    print(f"Warning (row {row_num}): Invalid value '{val}' for {field_name}. Valid values: {valid_values}")
            return values
        else:
            if value not in valid_values:
                print(f"Warning (row {row_num}): Invalid value '{value}' for {field_name}. Valid values: {valid_values}")
                return None
    
    return value

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
    default_matchmaker = Matchmaker.query.filter_by(email="default@example.com").first()
    if not default_matchmaker:
        default_matchmaker = Matchmaker(
            name="Default Matchmaker",
            email="default@example.com",
            password_hash=generate_password_hash("temppassword123")
        )
        db.session.add(default_matchmaker)
        db.session.flush()
    
    return default_matchmaker

def create_user_from_row(row_data, row_num):
    """Create a user and all related profiles from Excel row data"""
    errors = []
    
    # Extract and validate user data
    user_data = {}
    for excel_col, db_field in COLUMN_MAPPING['user'].items():
        if excel_col in row_data:
            value = row_data[excel_col]
            
            if db_field == 'email':
                if pd.isna(value) or not validate_email(str(value)):
                    errors.append(f"Invalid or missing email")
                    continue
                # Check for duplicate email
                existing_user = User.query.filter_by(email=str(value)).first()
                if existing_user:
                    errors.append(f"User with email {value} already exists")
                    continue
            elif db_field == 'dob':
                try:
                    value = parse_date(value)
                except ValueError as e:
                    errors.append(f"Invalid date format for Date of Birth: {e}")
                    continue
            elif db_field == 'gender':
                value = validate_field_value('gender', value, row_num)
                if not value:
                    errors.append("Invalid or missing gender")
                    continue
            
            if not pd.isna(value) and value != '':
                user_data[db_field] = value
    
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
    for excel_col, db_field in COLUMN_MAPPING['religious'].items():
        if excel_col in row_data:
            value = validate_field_value(db_field, row_data[excel_col], row_num)
            if value is not None:
                religious_data[db_field] = value
    
    if len(religious_data) > 1:  # More than just user_id
        religious_profile = ReligiousProfile(**religious_data)
        db.session.add(religious_profile)
    
    # Create background preferences
    background_data = {'user_id': user.id}
    for excel_col, db_field in COLUMN_MAPPING['background'].items():
        if excel_col in row_data:
            value = row_data[excel_col]
            if db_field == 'max_partner_age':
                try:
                    value = int(value) if not pd.isna(value) else None
                except (ValueError, TypeError):
                    print(f"Warning (row {row_num}): Invalid max partner age, skipping")
                    continue
            else:
                value = validate_field_value(db_field, value, row_num)
            
            if value is not None:
                background_data[db_field] = value
    
    if len(background_data) > 1:  # More than just user_id
        background_preferences = BackgroundPreferences(**background_data)
        db.session.add(background_preferences)
    
    # Create lifestyle preferences
    lifestyle_data = {'user_id': user.id}
    for excel_col, db_field in COLUMN_MAPPING['lifestyle'].items():
        if excel_col in row_data:
            value = validate_field_value(db_field, row_data[excel_col], row_num)
            if value is not None:
                lifestyle_data[db_field] = value
    
    if len(lifestyle_data) > 1:  # More than just user_id
        lifestyle_preferences = LifestylePreferences(**lifestyle_data)
        db.session.add(lifestyle_preferences)
    
    return user, []

def import_from_excel(file_path, matchmaker_email=None, dry_run=False):
    """Import users from Excel file"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        print(f"Found {len(df)} rows in Excel file")
        
        # Print available columns
        print(f"Available columns: {list(df.columns)}")
        
        # Find matchmaker
        matchmaker = find_or_create_matchmaker(matchmaker_email)
        
        success_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            row_num = index + 2  # Excel row number (accounting for header)
            
            try:
                user, errors = create_user_from_row(row.to_dict(), row_num)
                
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
        print(f"Error reading Excel file: {str(e)}")
        return False
    
    return True

def print_column_mapping():
    """Print the expected Excel column names"""
    print("Expected Excel Column Names:")
    print("=" * 50)
    
    print("\nUser Information (Required: Name, Email, Gender):")
    for excel_col in COLUMN_MAPPING['user'].keys():
        required = " (REQUIRED)" if excel_col in ['Name', 'Email', 'Gender'] else ""
        print(f"  - {excel_col}{required}")
    
    print("\nReligious Profile (All Optional):")
    for excel_col in COLUMN_MAPPING['religious'].keys():
        print(f"  - {excel_col}")
    
    print("\nBackground Preferences (All Optional):")
    for excel_col in COLUMN_MAPPING['background'].keys():
        print(f"  - {excel_col}")
    
    print("\nLifestyle Preferences (All Optional):")
    for excel_col in COLUMN_MAPPING['lifestyle'].keys():
        print(f"  - {excel_col}")
    
    print("\nNotes:")
    print("- Date of Birth should be in YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY format")
    print("- Array fields (like Languages, Ranked Activities) should be comma-separated")
    print("- Height should be in format like \"5'8\\\"\"")
    print("- Max Partner Age should be a number")

def main():
    parser = argparse.ArgumentParser(description='Import applicants from Excel file to SPARC database')
    parser.add_argument('excel_file', nargs='?', help='Path to Excel file')
    parser.add_argument('--matchmaker-email', '-m', help='Email of the matchmaker to assign users to')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Run without saving to database')
    parser.add_argument('--show-columns', '-c', action='store_true', help='Show expected column names and exit')
    
    args = parser.parse_args()
    
    if args.show_columns:
        print_column_mapping()
        return
    
    if not args.excel_file:
        print("Error: Excel file path is required")
        print("Usage: python import_from_excel.py path/to/file.xlsx")
        print("Use --show-columns to see expected column names")
        return
    
    if not os.path.exists(args.excel_file):
        print(f"Error: File {args.excel_file} does not exist")
        return
    
    with app.app_context():
        print(f"Starting import from {args.excel_file}")
        if args.dry_run:
            print("DRY RUN MODE - No data will be saved")
        if args.matchmaker_email:
            print(f"Assigning users to matchmaker: {args.matchmaker_email}")
        
        import_from_excel(args.excel_file, args.matchmaker_email, args.dry_run)

if __name__ == "__main__":
    main()
