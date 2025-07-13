# Excel Import Guide for SPARC Applicants

This guide explains how to use the Excel import functionality to add applicants to the SPARC database.

## Quick Start

1. **Create/Use Excel Template**: Run `python create_excel_template.py` to generate a template with all expected columns
2. **Fill in Your Data**: Add your applicant data to the Excel file
3. **Import to Database**: Run `python import_from_excel.py your_file.xlsx` to import the data

## Files Included

- `import_from_excel.py` - Main import script
- `create_excel_template.py` - Creates sample Excel template
- `applicant_import_template.xlsx` - Generated template file (after running create script)

## Usage Examples

### Show Expected Column Names
```bash
python import_from_excel.py --show-columns
```

### Test Import (Dry Run)
```bash
python import_from_excel.py applicants.xlsx --dry-run
```

### Import with Specific Matchmaker
```bash
python import_from_excel.py applicants.xlsx --matchmaker-email matchmaker@example.com
```

### Full Import
```bash
python import_from_excel.py applicants.xlsx
```

## Excel File Requirements

### Required Columns
- **Name** - Full name of the applicant
- **Email** - Must be unique and valid email format
- **Gender** - Must be "Male" or "Female"

### Optional Columns
All other columns are optional. The script will create profiles with whatever data is provided.

### Date Format
Date of Birth can be in any of these formats:
- YYYY-MM-DD (recommended)
- MM/DD/YYYY
- DD/MM/YYYY

### Array Fields (Comma-Separated)
These fields accept multiple values separated by commas:
- Languages
- Cultural Background  
- Ranked Activities
- Relationship Traits
- Ranked Priorities

Example: "English, Hebrew, Spanish"

## Column Categories

### User Information (11 columns)
- Name *(required)*
- Email *(required)*
- Phone
- Gender *(required)*
- Date of Birth
- Hometown
- Current Location
- Height (format: 5'8")
- Occupation
- Education Level
- Schools

### Religious Profile (11 columns)
- Cultural Background
- Languages
- Shabbat Observance
- Kosher Observance
- Jewish Learning
- Synagogue Attendance
- Childrens Education
- Shomer Negiah
- Male Partner Preference (for male users)
- Prayer Habits
- Religious Growth

### Background Preferences (8 columns)
- Convert Status
- Marital Status
- Children
- Aliyah
- Partner Background
- Min Partner Height (for male users)
- Max Partner Age (number)
- Photo URL

### Lifestyle Preferences (9 columns)
- Ranked Activities
- Living Environment
- Conflict Style
- Life Focus
- Activity Level
- Alcohol
- Smoking
- Relationship Traits
- Ranked Priorities

## Valid Values

The script validates certain fields against predefined lists. Invalid values will generate warnings but won't stop the import. See the script's `VALID_VALUES` dictionary for complete lists.

### Common Valid Values

**Gender**: Male, Female

**Education Level**: High School or Equivalent, Associates Degree, Bachelors Degree, Masters, PHD, Other

**Shabbat Observance**: 
- Shomer Shabbat - Fully Observant
- Traditional - Lightly Observant. Celebrates/Observes every week, but flexible with electricity
- Traditional - Celebrates/Observes weekly, but drives and cooks
- Spiritual - Occasionally has Friday/Shabbat Dinner night dinner
- Do not observe or celebrate

**Kosher Observance**:
- Strictly Kosher
- Kosher Home: eat out Vegan/Sushi
- Kosher Home: eat out Dairy
- Kosher Home: eat out everything
- Don't Keep Kosher

## Error Handling

The script will:
- Skip rows with missing required fields
- Show warnings for invalid values
- Continue processing other rows even if some fail
- Provide a summary of successes and errors

## Matchmaker Assignment

- If no matchmaker email is specified, users are assigned to a default matchmaker
- If specified matchmaker doesn't exist, a new one is created
- All users in the Excel file are assigned to the same matchmaker

## Database Safety

- **Dry Run Mode**: Use `--dry-run` to test without saving to database
- **Duplicate Prevention**: Email addresses must be unique
- **Transaction Safety**: If an error occurs, the current row is skipped but others continue

## Troubleshooting

### Common Issues

1. **"Invalid or missing email"** - Check email format and uniqueness
2. **"Invalid date format"** - Use YYYY-MM-DD format for dates
3. **"User with email X already exists"** - Email addresses must be unique
4. **"Invalid value for field"** - Check against valid values list

### Getting Help

Run with `--show-columns` to see all expected column names and requirements.

## Example Workflow

1. Generate template:
   ```bash
   python create_excel_template.py
   ```

2. Edit the generated `applicant_import_template.xlsx` file:
   - Delete sample rows
   - Add your applicant data
   - Fill in required columns (Name, Email, Gender)
   - Add optional data as available

3. Test the import:
   ```bash
   python import_from_excel.py applicant_import_template.xlsx --dry-run
   ```

4. Fix any errors shown, then do the real import:
   ```bash
   python import_from_excel.py applicant_import_template.xlsx
   ```

## Notes

- The script creates complete user profiles including religious, background, and lifestyle preferences
- Empty columns are ignored - you don't need to fill every field
- The script is designed to be flexible and handle incomplete data gracefully
- All imported users can be identified by looking for the applicants table relationships
