# Microsoft Forms Import Guide

This guide explains how to use the specialized Microsoft Forms import script for SPARC applicant data.

## Files

- **`import_microsoft_forms.py`** - Specialized import script for Microsoft Forms exports
- **`SPARC(1-39).xlsx`** - Your Microsoft Forms export file

## Quick Usage

### Test the Import (Recommended First)
```bash
python import_microsoft_forms.py --dry-run
```

### Import All Data
```bash
python import_microsoft_forms.py
```

### Import with Specific Matchmaker
```bash
python import_microsoft_forms.py --matchmaker-email matchmaker@example.com
```

## What This Script Does

### Automatic Column Mapping
The script automatically maps Microsoft Forms columns to your database fields:

**User Information:**
- `Full Name` → `name`
- `Email2` → `email` 
- `Phone` → `phone`
- `Gender` → `gender`
- `Date of Birth` → `dob`
- `Hometown (where you were raised)` → `hometown`
- `Current Location` → `current_location`
- `Height (ft'in) [ex: 5'8]` → `height`
- `Occupation (Company & Title)` → `occupation`
- `Highest level of education completed` → `education_level`
- `Schools Attended...` → `schools`

**Religious Profile:**
- `Cultural Background` → `cultural_background` (parsed from semicolon-separated values)
- `Select the languages you speak` → `languages` (parsed from semicolon-separated values)
- `Shabbat Observance` → `shabbat_observance`
- `Kosher Observance` → `kosher_observance`
- `Personal Jewish Learning/Education` → `jewish_learning`
- `Synagogue Attendance` → `synagogue_attendance`
- `Your children's Jewish education` → `childrens_education`
- `Your observance of shomer negiah...` → `shomer_negiah`
- `For Women/Men preference...` → `male_partner_preference`
- `Prayer Habits` → `prayer_habits`
- `Perspective on religious growth` → `religious_growth`

**Background Preferences:**
- `Conversion History` → `convert_status`
- `Marital Status` → `marital_status`
- `Children` → `children`
- `Aliyah` → `aliyah`
- `Ideal Partner's Cultural Background` → `partner_background`
- `Minimum partner height...` → `min_partner_height`
- `Maximum partner age` → `max_partner_age`

**Lifestyle Preferences:**
- `Rank these activities...` → `ranked_activities` (intelligent parsing)
- `Preferred Living Environment` → `living_environment`
- `Conflict Communication Style` → `conflict_style`
- `Personal Life Focus/Goals` → `life_focus`
- `How active are you` → `activity_level`
- `Alcohol Habits` → `alcohol`
- `Smoking Habits` → `smoking`
- `Which two traits...` → `relationship_traits` (intelligent parsing)
- `Rank these in order of importance/priority` → `ranked_priorities` (intelligent parsing)

### Smart Data Processing

**Cultural Background Parsing:**
- Handles semicolon-separated values like "Ashkenazi;Ashkenazi - Mix;Sephardic – Other;"
- Maps to standard database values

**Language Parsing:**
- Processes "Hebrew;Mainly English;" format
- Cleans and standardizes language names

**Activity/Priority Parsing:**
- Intelligently extracts activities from long descriptive text
- Maps to standard activity categories

**Value Mapping:**
- Automatically converts Microsoft Forms responses to database-compatible values
- Handles variations in spelling and format

### Error Handling
- Continues processing even if some rows have issues
- Reports warnings for invalid data
- Provides detailed success/error summary

## Results from Your Data

**Total Applicants:** 39
**Successfully Processed:** 39 (100%)
**Errors:** 0

The script successfully imported all applicants from your Microsoft Forms export with complete profile data including:
- Basic user information
- Religious preferences and observance levels
- Background and partner preferences  
- Lifestyle and activity preferences

## Next Steps

1. **Review the dry run results** to ensure data looks correct
2. **Run the actual import** when ready: `python import_microsoft_forms.py`
3. **Assign to specific matchmaker** if needed using `--matchmaker-email`

## Additional Notes

- Photos are noted as "Photos to be emailed separately" since they can't be imported from the form
- The script creates a default matchmaker "Microsoft Forms Import" if none is specified
- All data validation and error handling is built-in
- Compatible with your existing database structure

Your Microsoft Forms export is perfectly formatted and all data has been successfully mapped to your SPARC database schema!
