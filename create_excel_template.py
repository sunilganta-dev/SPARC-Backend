"""
Create a sample Excel template for importing applicants.
This script generates an Excel file with all the expected column headers
and a few sample rows to demonstrate the format.
"""

import pandas as pd
from datetime import datetime, date

def create_sample_excel():
    """Create a sample Excel file with proper column headers and example data"""
    
    # Define all columns based on the import script mapping
    columns = [
        # User information
        'Name', 'Email', 'Phone', 'Gender', 'Date of Birth', 'Hometown', 
        'Current Location', 'Height', 'Occupation', 'Education Level', 'Schools',
        
        # Religious profile  
        'Cultural Background', 'Languages', 'Shabbat Observance', 'Kosher Observance',
        'Jewish Learning', 'Synagogue Attendance', 'Childrens Education', 'Shomer Negiah',
        'Male Partner Preference', 'Prayer Habits', 'Religious Growth',
        
        # Background preferences
        'Convert Status', 'Marital Status', 'Children', 'Aliyah', 'Partner Background',
        'Min Partner Height', 'Max Partner Age', 'Photo URL',
        
        # Lifestyle preferences
        'Ranked Activities', 'Living Environment', 'Conflict Style', 'Life Focus',
        'Activity Level', 'Alcohol', 'Smoking', 'Relationship Traits', 'Ranked Priorities'
    ]
    
    # Sample data rows
    sample_data = [
        {
            'Name': 'David Cohen',
            'Email': 'david.cohen@example.com',
            'Phone': '555-123-4567',
            'Gender': 'Male',
            'Date of Birth': '1990-05-15',
            'Hometown': 'New York, NY',
            'Current Location': 'New York, NY',
            'Height': '5\'10"',
            'Occupation': 'Software Engineer at Google',
            'Education Level': 'Bachelors Degree',
            'Schools': 'Yeshiva University, NYU',
            'Cultural Background': 'Ashkenazi',
            'Languages': 'English, Hebrew',
            'Shabbat Observance': 'Shomer Shabbat - Fully Observant',
            'Kosher Observance': 'Strictly Kosher',
            'Jewish Learning': 'Daily',
            'Synagogue Attendance': 'Weekly',
            'Childrens Education': 'Essential and non-negotiable',
            'Shomer Negiah': 'Am fully shomer negiah',
            'Male Partner Preference': 'Strictly wears skirts and plans to cover hair',
            'Prayer Habits': 'Daven with a minyan consistently',
            'Religious Growth': 'Looking to grow',
            'Convert Status': 'I am not a convert',
            'Marital Status': 'Never married',
            'Children': 'Want Children',
            'Aliyah': 'Open',
            'Partner Background': 'Same as Self',
            'Min Partner Height': '5\'2"',
            'Max Partner Age': 28,
            'Photo URL': 'https://example.com/photo1.jpg',
            'Ranked Activities': 'Educational Activities, Social Activities, Physical Activities',
            'Living Environment': 'Specific City/Town',
            'Conflict Style': 'Direct and open',
            'Life Focus': 'Family/community oriented balance',
            'Activity Level': 'Active (3-4 times per week)',
            'Alcohol': 'Never',
            'Smoking': 'Never',
            'Relationship Traits': 'Mutual consideration/respect, Communication',
            'Ranked Priorities': 'Religion, Family, Partner Satisfaction, Career, Self-Satisfaction, Friends'
        },
        {
            'Name': 'Sarah Goldberg',
            'Email': 'sarah.goldberg@example.com',
            'Phone': '555-987-6543',
            'Gender': 'Female',
            'Date of Birth': '1992-03-22',
            'Hometown': 'Los Angeles, CA',
            'Current Location': 'Los Angeles, CA',
            'Height': '5\'4"',
            'Occupation': 'Teacher at Jewish Day School',
            'Education Level': 'Masters',
            'Schools': 'Stern College, Columbia University',
            'Cultural Background': 'Ashkenazi - Mix',
            'Languages': 'English, Hebrew, Spanish',
            'Shabbat Observance': 'Traditional - Lightly Observant. Celebrates/Observes every week, but flexible with electricity',
            'Kosher Observance': 'Kosher Home: eat out Vegan/Sushi',
            'Jewish Learning': 'Weekly',
            'Synagogue Attendance': 'Weekly',
            'Childrens Education': 'Important but can be provided outside of school',
            'Shomer Negiah': 'Am fully shomer negiah',
            'Prayer Habits': 'Davens Daily',
            'Religious Growth': 'Open to growth',
            'Convert Status': 'I am not a convert',
            'Marital Status': 'Never married',
            'Children': 'Want Children',
            'Aliyah': 'No',
            'Partner Background': 'Open to all',
            'Max Partner Age': 35,
            'Photo URL': 'https://example.com/photo2.jpg',
            'Ranked Activities': 'Creative Activities, Cultural Activities, Educational Activities',
            'Living Environment': 'Slightly open to nearby cities/states',
            'Conflict Style': 'Calm and reflective',
            'Life Focus': 'Family/community oriented balance',
            'Activity Level': 'Somewhat Active (1-2 times per week)',
            'Alcohol': 'Socially',
            'Smoking': 'Never',
            'Relationship Traits': 'Peacefulness, Accepting imperfections',
            'Ranked Priorities': 'Family, Religion, Partner Satisfaction, Self-Satisfaction, Career, Friends'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(sample_data, columns=columns)
    
    # Save to Excel
    filename = 'applicant_import_template.xlsx'
    df.to_excel(filename, index=False)
    
    print(f"Sample Excel template created: {filename}")
    print(f"Contains {len(columns)} columns and {len(sample_data)} sample rows")
    print("\nColumn categories:")
    print("- User Information: 11 columns (Name, Email, Gender are required)")
    print("- Religious Profile: 11 columns")
    print("- Background Preferences: 8 columns") 
    print("- Lifestyle Preferences: 9 columns")
    print("\nYou can:")
    print("1. Delete the sample rows and add your own data")
    print("2. Leave columns empty if you don't have the data")
    print("3. Use comma-separated values for array fields like 'Languages' or 'Ranked Activities'")

if __name__ == "__main__":
    create_sample_excel()
