"""
Simple test script to verify the matchmaker API endpoints are working correctly.
"""

import requests
import json

API_BASE = "http://127.0.0.1:5005/api/matchmaker"

def test_get_profile():
    """Test the GET /api/matchmaker/profile endpoint"""
    print("Testing GET /api/matchmaker/profile...")
    try:
        response = requests.get(f"{API_BASE}/profile")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            profile = response.json()
            print(f"Profile Name: {profile.get('name')}")
            print(f"Organization: {profile.get('organization')}")
            print(f"Experience: {profile.get('experience_years')} years")
            print(f"Specializations: {profile.get('specializations')}")
            return profile
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_update_profile():
    """Test the PUT /api/matchmaker/profile endpoint"""
    print("\nTesting PUT /api/matchmaker/profile...")
    
    update_data = {
        "name": "Sarah Cohen-Levy",
        "phone": "+1 (212) 555-7891",
        "experience_years": 9,
        "bio": "Updated bio: Expert matchmaker with expanded experience.",
        "specializations": ["religious", "cultural", "young professionals", "modern orthodox", "graduate professionals", "second marriages"]
    }
    
    try:
        response = requests.put(
            f"{API_BASE}/profile", 
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Message: {result.get('message')}")
            print(f"Updated Name: {result.get('profile', {}).get('name')}")
            print(f"Updated Experience: {result.get('profile', {}).get('experience_years')} years")
            return result
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_stats():
    """Test the GET /api/matchmaker/stats endpoint"""
    print("\nTesting GET /api/matchmaker/stats...")
    try:
        response = requests.get(f"{API_BASE}/stats")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"Total Applicants: {stats.get('applicants')}")
            print(f"Unique Users: {stats.get('unique_users')}")
            print(f"Matches: {stats.get('matches')}")
            print(f"Success Rate: {stats.get('success_rate')}%")
            return stats
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_activity():
    """Test the GET /api/matchmaker/activity endpoint"""
    print("\nTesting GET /api/matchmaker/activity...")
    try:
        response = requests.get(f"{API_BASE}/activity")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            activities = result.get('activities', [])
            print(f"Number of activities: {len(activities)}")
            for i, activity in enumerate(activities[:3]):  # Show first 3
                print(f"  {i+1}. {activity.get('title')}: {activity.get('description')}")
            return result
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("Testing Matchmaker API Endpoints")
    print("=" * 40)
    
    # Test all endpoints
    profile = test_get_profile()
    update_result = test_update_profile()
    stats = test_get_stats()
    activity = test_get_activity()
    
    # Test getting updated profile
    print("\nTesting updated profile...")
    updated_profile = test_get_profile()
    
    print("\n" + "=" * 40)
    if all([profile, update_result, stats, activity, updated_profile]):
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
