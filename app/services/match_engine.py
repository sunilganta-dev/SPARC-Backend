from app.models.user import User
from app.models.religion import ReligiousProfile
from app.models.background import BackgroundPreferences
from app.models.lifestyle import LifestylePreferences
from sqlalchemy import desc
from datetime import datetime
import math

# Dictionary to score compatibility for various fields
COMPATIBILITY_WEIGHTS = {
    # Higher weights indicate more important matching criteria
    "gender": 100,  # Must be opposite gender for matching
    "age": 5,
    "height": 2,
    "cultural_background": 4,
    "languages": 3,
    "shabbat_observance": 8,
    "kosher_observance": 8,
    "jewish_learning": 6,
    "synagogue_attendance": 5,
    "childrens_education": 7,
    "religious_growth": 6,
    "convert_status": 3,
    "marital_status": 4,
    "children": 7,
    "aliyah": 5,
    "conflict_style": 5,
    "life_focus": 6,
    "activity_level": 3,
    "alcohol": 3,
    "smoking": 4,
    "relationship_traits": 6,
    "ranked_priorities": 5
}

# Ranking systems for ordinal values
kosher_ranks = {
    "Strictly Kosher": 4,
    "Kosher Home: eat out Vegan/Sushi": 3,
    "Kosher Home: eat out Dairy": 2, 
    "Kosher Home: eat out everything": 1,
    "Don't Keep Kosher": 0
}

shabbat_ranks = {
    "Shomer Shabbat - Fully Observant": 4,
    "Traditional - Lightly Observant. Celebrates/Observes every week, but flexible with electricity": 3,
    "Traditional - Celebrates/Observes weekly, but drives and cooks": 2,
    "Spiritual - Occasionally has Friday/Shabbat Dinner night dinner": 1,
    "Do not observe or celebrate": 0
}

attendance_ranks = {
    "Daily": 4,
    "Weekly": 3,
    "Occasionally": 2,
    "Major holidays only": 1,
    "Rarely/Never": 0
}

learning_ranks = {
    "Daily": 4,
    "Multiple times a week": 3,
    "Weekly": 2,
    "Occasionally": 1,
    "Rarely/Never": 0
}

prayer_ranks = {
    "Daven with a minyan consistently": 4,
    "Davens 3x a day individually": 3,
    "Davens Daily": 2,
    "Weekly": 1,
    "Not often": 0
}

# Helper functions to calculate compatibility scores
def gender_compatibility(user_a, user_b):
    """Returns 1 if opposite gender, 0 if same gender"""
    if user_a.gender != user_b.gender:
        return 1
    return 0

def rank_compatibility(rank_a, rank_b, ranking_system):
    """Calculate compatibility based on ranked values"""
    if rank_a is None or rank_b is None:
        return 0.5  # Default middle value if data is missing
    
    a_rank = ranking_system.get(rank_a, -1)
    b_rank = ranking_system.get(rank_b, -1)
    
    if a_rank == -1 or b_rank == -1:
        return 0.5  # Default if invalid data
    
    # Calculate normalized similarity (0-1)
    max_diff = max(ranking_system.values()) - min(ranking_system.values())
    if max_diff == 0:
        return 1
    
    similarity = 1 - (abs(a_rank - b_rank) / max_diff)
    return similarity

def array_compatibility(array_a, array_b):
    """Calculate similarity between two arrays of strings"""
    if not array_a or not array_b:
        return 0.5  # Default if data is missing
    
    # Calculate Jaccard similarity
    intersection = len(set(array_a).intersection(set(array_b)))
    union = len(set(array_a).union(set(array_b)))
    
    if union == 0:
        return 0.5
    
    return intersection / union

def age_compatibility(dob_a, dob_b, max_age_pref=None):
    """Calculate age compatibility based on date of birth and preferences"""
    if dob_a is None or dob_b is None:
        return 0.5  # Default if data is missing
    
    age_a = calculate_age(dob_a)
    age_b = calculate_age(dob_b)
    
    # Simple age difference compatibility (10 year span is considered max difference)
    age_diff = abs(age_a - age_b)
    age_comp = max(0, 1 - (age_diff / 10))
    
    # If max age preference is specified
    if max_age_pref is not None:
        if age_b > max_age_pref:
            age_comp = 0
    
    return age_comp

def calculate_age(dob):
    """Calculate age from date of birth"""
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def height_compatibility(height_a, height_b, min_height_pref=None):
    """Calculate height compatibility including preferences"""
    if height_a is None or height_b is None:
        return 0.5  # Default if data is missing
    
    # Parse heights like 5'8" to inches
    try:
        inches_a = parse_height_to_inches(height_a)
        inches_b = parse_height_to_inches(height_b)
        
        # Men typically prefer women shorter than them, women typically prefer men taller
        if min_height_pref:
            min_inches = parse_height_to_inches(min_height_pref)
            if inches_b < min_inches:
                return 0
        
        # Calculate height difference compatibility (12 inches diff = 0 compatibility)
        height_diff = abs(inches_a - inches_b)
        return max(0, 1 - (height_diff / 12))
    except:
        return 0.5  # Default if parsing fails

def parse_height_to_inches(height_str):
    """Parse height string like 5'8" to total inches"""
    try:
        parts = height_str.replace('"', '').split("'")
        feet = int(parts[0])
        inches = int(parts[1]) if len(parts) > 1 else 0
        return (feet * 12) + inches
    except:
        return 65  # Default average height if parsing fails

def score_match(user_a, user_b):
    """Calculate overall match score between two users (0-100)"""
    
    # Initial checks for dealbreakers
    # Must be opposite gender (if not, return 0)
    if gender_compatibility(user_a, user_b) == 0:
        return 0

    # Calculate individual compatibility scores
    scores = {}
    
    # Basic profile compatibility
    scores["gender"] = gender_compatibility(user_a, user_b)
    scores["age"] = age_compatibility(user_a.dob, user_b.dob, 
                                     user_a.background.max_partner_age if hasattr(user_a, 'background') else None)
    scores["height"] = height_compatibility(user_a.height, user_b.height, 
                                           user_a.background.min_partner_height if hasattr(user_a, 'background') else None)
    
    # Religious compatibility
    if hasattr(user_a, 'religious_profile') and hasattr(user_b, 'religious_profile'):
        rel_a = user_a.religious_profile
        rel_b = user_b.religious_profile
        
        # Cultural compatibility
        scores["cultural_background"] = array_compatibility(
            rel_a.cultural_background, rel_b.cultural_background)
        
        # Language compatibility
        scores["languages"] = array_compatibility(
            rel_a.languages, rel_b.languages)
        
        # Religious observance compatibility
        scores["shabbat_observance"] = rank_compatibility(
            rel_a.shabbat_observance, rel_b.shabbat_observance, shabbat_ranks)
        
        scores["kosher_observance"] = rank_compatibility(
            rel_a.kosher_observance, rel_b.kosher_observance, kosher_ranks)
        
        scores["jewish_learning"] = rank_compatibility(
            rel_a.jewish_learning, rel_b.jewish_learning, learning_ranks)
        
        scores["synagogue_attendance"] = rank_compatibility(
            rel_a.synagogue_attendance, rel_b.synagogue_attendance, attendance_ranks)
        
        scores["prayer_habits"] = rank_compatibility(
            rel_a.prayer_habits, rel_b.prayer_habits, prayer_ranks)
        
        # Simple string matches (1 for exact match, 0.5 for partial, 0 for no match)
        scores["childrens_education"] = 1 if rel_a.childrens_education == rel_b.childrens_education else 0.5
        scores["religious_growth"] = 1 if rel_a.religious_growth == rel_b.religious_growth else 0.5
    
    # Background compatibility
    if hasattr(user_a, 'background') and hasattr(user_b, 'background'):
        bg_a = user_a.background
        bg_b = user_b.background
        
        scores["convert_status"] = 1 if bg_a.convert_status == bg_b.convert_status else 0.5
        scores["marital_status"] = 1 if bg_a.marital_status == bg_b.marital_status else 0.5
        scores["children"] = 1 if bg_a.children == bg_b.children else 0.5
        scores["aliyah"] = 1 if bg_a.aliyah == bg_b.aliyah else 0.5
    
    # Lifestyle compatibility
    if hasattr(user_a, 'lifestyle') and hasattr(user_b, 'lifestyle'):
        ls_a = user_a.lifestyle
        ls_b = user_b.lifestyle
        
        scores["conflict_style"] = 1 if ls_a.conflict_style == ls_b.conflict_style else 0.5
        scores["life_focus"] = 1 if ls_a.life_focus == ls_b.life_focus else 0.5
        scores["activity_level"] = 1 if ls_a.activity_level == ls_b.activity_level else 0.5
        scores["alcohol"] = 1 if ls_a.alcohol == ls_b.alcohol else 0.5
        scores["smoking"] = 1 if ls_a.smoking == ls_b.smoking else 0.5
        
        scores["relationship_traits"] = array_compatibility(
            ls_a.relationship_traits, ls_b.relationship_traits)
        
        scores["ranked_priorities"] = array_compatibility(
            ls_a.ranked_priorities, ls_b.ranked_priorities)
    
    # Calculate weighted score
    weighted_score = 0
    total_weight = 0
    
    for field, score in scores.items():
        weight = COMPATIBILITY_WEIGHTS.get(field, 1)
        weighted_score += score * weight
        total_weight += weight
    
    # Normalize to 0-100 scale
    if total_weight == 0:
        return 0
    
    final_score = (weighted_score / total_weight) * 100
    return round(final_score, 1)

def get_matches_for_user(user_id, limit=10):
    """Get top matches for a specific user"""
    user = User.query.get(user_id)
    if not user:
        return []
    
    # Get users of opposite gender
    if user.gender == "Male":
        potential_matches = User.query.filter_by(gender="Female").all()
    else:
        potential_matches = User.query.filter_by(gender="Male").all()
    
    # Calculate match scores
    matches = []
    for potential_match in potential_matches:
        if potential_match.id == user_id:
            continue
        
        match_score = score_match(user, potential_match)
        if match_score > 0:  # Only include non-zero matches
            matches.append({
                "user_id": potential_match.id,
                "name": potential_match.name,
                "score": match_score,
                "compatibility": get_compatibility_details(user, potential_match)
            })
    
    # Sort by score in descending order
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top N matches
    return matches[:limit]

def get_compatibility_details(user_a, user_b):
    """Get detailed compatibility breakdown between two users"""
    details = {}
    
    # Get compatibility details for key areas
    if hasattr(user_a, 'religious_profile') and hasattr(user_b, 'religious_profile'):
        rel_a = user_a.religious_profile
        rel_b = user_b.religious_profile
        
        details["religious_compatibility"] = {
            "score": round((
                rank_compatibility(rel_a.shabbat_observance, rel_b.shabbat_observance, shabbat_ranks) +
                rank_compatibility(rel_a.kosher_observance, rel_b.kosher_observance, kosher_ranks) +
                rank_compatibility(rel_a.jewish_learning, rel_b.jewish_learning, learning_ranks) +
                rank_compatibility(rel_a.synagogue_attendance, rel_b.synagogue_attendance, attendance_ranks)
            ) / 4 * 100),
            "details": {
                "shabbat": rel_a.shabbat_observance + " vs " + rel_b.shabbat_observance,
                "kosher": rel_a.kosher_observance + " vs " + rel_b.kosher_observance
            }
        }
    
    if hasattr(user_a, 'background') and hasattr(user_b, 'background'):
        details["family_compatibility"] = {
            "score": round((
                (1 if user_a.background.children == user_b.background.children else 0.5) +
                (1 if user_a.background.aliyah == user_b.background.aliyah else 0.5)
            ) / 2 * 100)
        }
    
    return details

def get_all_top_matches(limit_per_match=5, min_score=50):
    """Get all top matches across the entire system"""
    users = User.query.all()
    all_matches = []
    
    for user in users:
        user_matches = get_matches_for_user(user.id, limit=limit_per_match)
        # Filter by minimum score
        user_matches = [match for match in user_matches if match["score"] >= min_score]
        
        for match in user_matches:
            # Create a bidirectional match record
            match_record = {
                "user_a_id": user.id,
                "user_a_name": user.name,
                "user_b_id": match["user_id"],
                "user_b_name": match["name"],
                "score": match["score"],
                "compatibility": match.get("compatibility", {})
            }
            
            # Check if this match already exists in reverse
            exists = False
            for existing in all_matches:
                if (existing["user_a_id"] == match_record["user_b_id"] and 
                    existing["user_b_id"] == match_record["user_a_id"]):
                    exists = True
                    break
            
            if not exists:
                all_matches.append(match_record)
    
    # Sort by score
    all_matches.sort(key=lambda x: x["score"], reverse=True)
    return all_matches

def get_matchmaker_matches(matchmaker_id, limit=100):
    """Get matches that involve a matchmaker's applicants"""
    from app.models.matchmaker import Applicant
    
    # Get all applicants for this matchmaker
    applicants = Applicant.query.filter_by(shidduch_lady_id=matchmaker_id).all()
    applicant_ids = [a.user_id for a in applicants]
    
    if not applicant_ids:
        return []
    
    all_matches = []
    
    # For each applicant, get their matches
    for applicant_id in applicant_ids:
        user_matches = get_matches_for_user(applicant_id, limit=limit)
        
        applicant = User.query.get(applicant_id)
        if not applicant:
            continue
            
        for match in user_matches:
            match_record = {
                "applicant_id": applicant_id,
                "applicant_name": applicant.name,
                "match_id": match["user_id"],
                "match_name": match["name"],
                "score": match["score"],
                "compatibility": match.get("compatibility", {})
            }
            all_matches.append(match_record)
    
    # Sort by score
    all_matches.sort(key=lambda x: x["score"], reverse=True)
    return all_matches
