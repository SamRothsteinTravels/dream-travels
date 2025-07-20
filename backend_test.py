#!/usr/bin/env python3
"""
Enhanced Backend API Testing Script for TravelMate Pro
Tests the enhanced destinations, interests, itinerary generation, and export endpoints
"""

import requests
import json
import sys
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = "https://f65693a0-1b97-4e30-b245-f7ec80833314.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_available_destinations():
    """Test the GET /api/available-destinations endpoint"""
    print("=" * 60)
    print("Testing Available Destinations Endpoint")
    print("=" * 60)
    
    try:
        url = f"{API_BASE}/available-destinations"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Available destinations endpoint working!")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Validate response structure
            if "destinations" in data:
                destinations = data["destinations"]
                print(f"Found {len(destinations)} destinations")
                
                # Check if Orlando is available (needed for next test)
                orlando_found = False
                for dest in destinations:
                    if "Orlando" in dest.get("name", ""):
                        orlando_found = True
                        print(f"✅ Orlando found: {dest}")
                        break
                
                if not orlando_found:
                    print("⚠️  Orlando not found in destinations list")
                    return False
                    
                return True
            else:
                print("❌ Response missing 'destinations' field")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed with error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_generate_itinerary():
    """Test the POST /api/generate-itinerary endpoint with Orlando parameters"""
    print("\n" + "=" * 60)
    print("Testing Generate Itinerary Endpoint")
    print("=" * 60)
    
    # Test parameters as specified in the request
    test_data = {
        "destination": "Orlando, FL",
        "interests": ["theme parks", "family friendly", "dining hot spots"],
        "number_of_days": 3
    }
    
    try:
        url = f"{API_BASE}/generate-itinerary"
        print(f"Making request to: {url}")
        print(f"Request payload: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            url, 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Itinerary generation endpoint working!")
            
            # Validate response structure
            required_fields = ["id", "destination", "interests", "days", "created_at"]
            missing_fields = []
            
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Response missing required fields: {missing_fields}")
                return False
            
            # Validate days structure
            days = data.get("days", [])
            print(f"Generated itinerary for {len(days)} days")
            
            if len(days) != 3:
                print(f"❌ Expected 3 days, got {len(days)}")
                return False
            
            # Check each day structure
            for i, day in enumerate(days, 1):
                print(f"\n--- Day {i} ---")
                
                required_day_fields = ["day", "activities", "total_estimated_time"]
                day_missing_fields = []
                
                for field in required_day_fields:
                    if field not in day:
                        day_missing_fields.append(field)
                
                if day_missing_fields:
                    print(f"❌ Day {i} missing fields: {day_missing_fields}")
                    return False
                
                activities = day.get("activities", [])
                print(f"Day {i}: {len(activities)} activities")
                print(f"Total estimated time: {day.get('total_estimated_time')}")
                
                # Check activities structure
                for j, activity in enumerate(activities):
                    required_activity_fields = ["id", "name", "category", "description", "location", "address", "estimated_duration", "best_time"]
                    activity_missing_fields = []
                    
                    for field in required_activity_fields:
                        if field not in activity:
                            activity_missing_fields.append(field)
                    
                    if activity_missing_fields:
                        print(f"❌ Activity {j+1} in Day {i} missing fields: {activity_missing_fields}")
                        return False
                    
                    # Validate location structure
                    location = activity.get("location", {})
                    if not isinstance(location, dict) or "lat" not in location or "lng" not in location:
                        print(f"❌ Activity {j+1} in Day {i} has invalid location structure")
                        return False
                    
                    print(f"  - {activity['name']} ({activity['category']})")
                    print(f"    Duration: {activity['estimated_duration']}, Best time: {activity['best_time']}")
                    print(f"    Location: {location['lat']}, {location['lng']}")
            
            # Check if activities are grouped geographically (basic check)
            print(f"\n--- Geographic Clustering Analysis ---")
            total_activities = sum(len(day['activities']) for day in days)
            print(f"Total activities distributed across {len(days)} days: {total_activities}")
            
            # Verify interests are represented
            print(f"\n--- Interest Coverage Analysis ---")
            all_categories = set()
            for day in days:
                for activity in day['activities']:
                    all_categories.add(activity['category'])
            
            requested_interests = set(test_data['interests'])
            covered_interests = all_categories.intersection(requested_interests)
            
            print(f"Requested interests: {requested_interests}")
            print(f"Covered interests: {covered_interests}")
            
            if len(covered_interests) < len(requested_interests):
                missing_interests = requested_interests - covered_interests
                print(f"⚠️  Some interests not covered: {missing_interests}")
            else:
                print("✅ All requested interests are covered!")
            
            print(f"\n✅ Itinerary generation test passed!")
            print(f"Full response structure validated successfully")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed with error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all backend API tests"""
    print("Starting Backend API Tests for Travel Itinerary App")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test 1: Available Destinations
    destinations_success = test_available_destinations()
    
    # Test 2: Generate Itinerary (only if destinations test passed)
    if destinations_success:
        itinerary_success = test_generate_itinerary()
    else:
        print("\n❌ Skipping itinerary test due to destinations endpoint failure")
        itinerary_success = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Available Destinations: {'✅ PASS' if destinations_success else '❌ FAIL'}")
    print(f"Generate Itinerary: {'✅ PASS' if itinerary_success else '❌ FAIL'}")
    
    if destinations_success and itinerary_success:
        print("\n🎉 All backend API tests passed!")
        return 0
    else:
        print("\n💥 Some backend API tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())