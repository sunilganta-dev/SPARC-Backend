"""
Script to add profile fields to the Matchmaker table.
This adds the new columns needed for the enhanced profile functionality.
"""

import sys
import os

# Add the application root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import db, app

def add_matchmaker_profile_fields():
    """Add new profile fields to the Matchmaker table"""
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('shidduch_ladies')]
            
            new_columns = [
                'organization',
                'phone', 
                'location',
                'experience_years',
                'bio',
                'website',
                'specializations',
                'social_media',
                'created_at',
                'updated_at'
            ]
            
            # Add columns that don't exist
            with db.engine.connect() as connection:
                for column in new_columns:
                    if column not in existing_columns:
                        if column == 'experience_years':
                            connection.execute(db.text(f'ALTER TABLE shidduch_ladies ADD COLUMN {column} INTEGER DEFAULT 0'))
                        elif column in ['bio', 'specializations', 'social_media']:
                            connection.execute(db.text(f'ALTER TABLE shidduch_ladies ADD COLUMN {column} TEXT'))
                        elif column in ['created_at', 'updated_at']:
                            connection.execute(db.text(f'ALTER TABLE shidduch_ladies ADD COLUMN {column} TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
                        else:
                            connection.execute(db.text(f'ALTER TABLE shidduch_ladies ADD COLUMN {column} VARCHAR(255)'))
                        print(f"Added column: {column}")
                        connection.commit()
                    else:
                        print(f"Column {column} already exists")
            
            print("Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            return False
        
        return True

if __name__ == "__main__":
    success = add_matchmaker_profile_fields()
    if success:
        print("Profile fields added successfully!")
    else:
        print("Migration failed!")
