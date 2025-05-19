"""
Create all database tables for the SPARC application.
This script directly creates the tables using SQLAlchemy's create_all() method.

Usage:
    python create_tables.py
"""

import sys
import os

# Add the application root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, app
# Import all models to ensure they're registered with SQLAlchemy
from app.models import User, ReligiousProfile, BackgroundPreferences, LifestylePreferences, Matchmaker, Applicant

def check_tables():
    """Check which tables exist in the database"""
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()
    
    print(f"Current database: {db.engine.url}")
    print(f"Existing tables: {existing_tables if existing_tables else 'None'}")
    
    # Define expected tables
    expected_tables = ['users', 'religious_profile', 'background_preferences', 
                       'lifestyle_preferences', 'shidduch_ladies', 'applicants']
    
    missing_tables = [table for table in expected_tables if table not in existing_tables]
    if missing_tables:
        print(f"Missing tables: {missing_tables}")
        return False
    else:
        print("All expected tables exist.")
        return True

def create_tables():
    """Create all tables in the database"""
    try:
        print("Creating all database tables...")
        db.create_all()
        print("Tables created successfully!")
        check_tables()
        return True
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        return False

def main():
    """Run the table creation script"""
    with app.app_context():
        print("Checking existing tables...")
        tables_exist = check_tables()
        
        if not tables_exist:
            confirm = input("Some tables are missing. Create them now? (y/n): ")
            if confirm.lower() == 'y':
                create_tables()
            else:
                print("Operation cancelled.")
        else:
            print("All tables already exist. No action needed.")

if __name__ == "__main__":
    main() 