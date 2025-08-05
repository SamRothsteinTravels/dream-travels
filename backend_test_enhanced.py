#!/usr/bin/env python3
"""
Enhanced Backend API Testing Script for Dream Travels
Tests the enhanced destinations, interests, itinerary generation, and export endpoints
"""

import requests
import json
import sys
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = "https://b9e0b037-88d9-486a-9164-512092719ad2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_enhanced_destinations_endpoint():
    """Test the enhanced GET /api/destinations endpoint with filters"""
    print("=" * 60)
    print("Testing Enhanced Destinations Endpoint")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Get all destinations
    try:
        print("\n--- Test 1: All destinations ---")
        url = f"{API_BASE}/destinations"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ All destinations endpoint working!")
            
            # Validate response structure
            required_fields = ["destinations", "total", "regions"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Response missing required fields: {missing_fields}")
                test_results.append(False)
            else:
                destinations = data["destinations"]
                print(f"Found {len(destinations)} destinations")
                print(f"Available regions: {data['regions']}")
                
                # Check destination structure
                if destinations:
                    sample_dest = destinations[0]
                    required_dest_fields = ["key", "name", "country", "region", "description", "solo_female_safety", "safety_notes", "hidden_gem"]
                    missing_dest_fields = [field for field in required_dest_fields if field not in sample_dest]
                    
                    if missing_dest_fields:
                        print(f"❌ Destination missing fields: {missing_dest_fields}")
                        test_results.append(False)
                    else:
                        print(f"✅ Destination structure validated")
                        test_results.append(True)
                else:
                    print("❌ No destinations returned")
                    test_results.append(False)
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Test 1 failed with error: {e}")
        test_results.append(False)
    
    # Test 2: Filter by region (Europe)
    try:
        print("\n--- Test 2: Filter by region (Europe) ---")
        url = f"{API_BASE}/destinations?region=Europe"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            destinations = data["destinations"]
            print(f"Found {len(destinations)} European destinations")
            
            # Verify all destinations are from Europe
            all_europe = all(dest["region"] == "Europe" for dest in destinations)
            if all_europe:
                print("✅ Region filter working correctly")
                test_results.append(True)
            else:
                print("❌ Region filter not working - non-European destinations found")
                test_results.append(False)
        else:
            print(f"❌ Request failed with status {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Test 2 failed with error: {e}")
        test_results.append(False)
    
    # Test 3: Filter by solo female safe destinations
    try:
        print("\n--- Test 3: Solo female safe destinations ---")
        url = f"{API_BASE}/destinations?solo_female_safe=true"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            destinations = data["destinations"]
            print(f"Found {len(destinations)} solo female safe destinations")
            
            # Verify all destinations have safety rating >= 4
            all_safe = all(dest["solo_female_safety"] >= 4 for dest in destinations)
            if all_safe:
                print("✅ Solo female safety filter working correctly")
                test_results.append(True)
            else:
                print("❌ Solo female safety filter not working")
                test_results.append(False)
        else:
            print(f"❌ Request failed with status {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Test 3 failed with error: {e}")
        test_results.append(False)
    
    # Test 4: Filter by hidden gems
    try:
        print("\n--- Test 4: Hidden gems only ---")
        url = f"{API_BASE}/destinations?hidden_gems=true"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            destinations = data["destinations"]
            print(f"Found {len(destinations)} hidden gem destinations")
            
            # Verify all destinations are hidden gems
            all_hidden = all(dest["hidden_gem"] == True for dest in destinations)
            if all_hidden:
                print("✅ Hidden gems filter working correctly")
                test_results.append(True)
            else:
                print("❌ Hidden gems filter not working")
                test_results.append(False)
        else:
            print(f"❌ Request failed with status {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Test 4 failed with error: {e}")
        test_results.append(False)
    
    # Test 5: Filter by minimum safety rating
    try:
        print("\n--- Test 5: Minimum safety rating (5) ---")
        url = f"{API_BASE}/destinations?min_safety_rating=5"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            destinations = data["destinations"]
            print(f"Found {len(destinations)} destinations with safety rating 5")
            
            # Verify all destinations have safety rating = 5
            all_max_safe = all(dest["solo_female_safety"] == 5 for dest in destinations)
            if all_max_safe:
                print("✅ Minimum safety rating filter working correctly")
                test_results.append(True)
            else:
                print("❌ Minimum safety rating filter not working")
                test_results.append(False)
        else:
            print(f"❌ Request failed with status {response.status_code}")
            test_results.append(False)
            
    except Exception as e:
        print(f"❌ Test 5 failed with error: {e}")
        test_results.append(False)
    
    return all(test_results)

def test_enhanced_interests_endpoint():
    """Test the enhanced GET /api/interests endpoint"""
    print("\n" + "=" * 60)
    print("Testing Enhanced Interests Endpoint")
    print("=" * 60)
    
    try:
        url = f"{API_BASE}/interests"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Interests endpoint working!")
            
            # Validate response structure
            required_fields = ["interests", "solo_female_guidelines"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Response missing required fields: {missing_fields}")
                return False
            
            interests = data["interests"]
            print(f"Found {len(interests)} interest categories")
            
            # Check if solo female interest is included
            if "solo female" in interests:
                print("✅ Solo female interest category found")
            else:
                print("❌ Solo female interest category missing")
                return False
            
            # Check solo female guidelines
            guidelines = data["solo_female_guidelines"]
            if isinstance(guidelines, dict) and "general_tips" in guidelines:
                print("✅ Solo female guidelines included")
                print(f"Guidelines categories: {list(guidelines.keys())}")
            else:
                print("❌ Solo female guidelines missing or invalid")
                return False
            
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Interests endpoint test failed with error: {e}")
        return False

def test_enhanced_itinerary_generation():
    """Test the enhanced POST /api/generate-itinerary endpoint with solo female features"""
    print("\n" + "=" * 60)
    print("Testing Enhanced Itinerary Generation")
    print("=" * 60)
    
    # Test parameters as specified in the review request
    test_data = {
        "destination": "Tokyo, Japan",
        "interests": ["cultural experiences", "solo female", "family friendly"],
        "number_of_days": 3,
        "solo_female_traveler": True
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
            print("✅ Enhanced itinerary generation endpoint working!")
            
            # Validate enhanced response structure
            required_fields = ["id", "destination", "interests", "days", "created_at", "solo_female_safety_rating", "safety_notes"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Response missing required fields: {missing_fields}")
                return False
            
            # Check solo female safety features
            if data["solo_female_safety_rating"]:
                print(f"✅ Solo female safety rating: {data['solo_female_safety_rating']}/5")
            else:
                print("❌ Solo female safety rating missing")
                return False
            
            if data["safety_notes"]:
                print(f"✅ Safety notes included: {data['safety_notes'][:100]}...")
            else:
                print("❌ Safety notes missing")
                return False
            
            # Validate days structure with safety features
            days = data.get("days", [])
            print(f"Generated itinerary for {len(days)} days")
            
            if len(days) != 3:
                print(f"❌ Expected 3 days, got {len(days)}")
                return False
            
            # Check each day for safety notes
            for i, day in enumerate(days, 1):
                print(f"\n--- Day {i} ---")
                
                required_day_fields = ["day", "activities", "total_estimated_time", "safety_notes"]
                day_missing_fields = [field for field in required_day_fields if field not in day]
                
                if day_missing_fields:
                    print(f"❌ Day {i} missing fields: {day_missing_fields}")
                    return False
                
                activities = day.get("activities", [])
                print(f"Day {i}: {len(activities)} activities")
                print(f"Total estimated time: {day.get('total_estimated_time')}")
                
                if day.get("safety_notes"):
                    print(f"✅ Safety notes for Day {i}: {day['safety_notes'][:50]}...")
                else:
                    print(f"❌ Safety notes missing for Day {i}")
                    return False
                
                # Check activities for solo female features
                for j, activity in enumerate(activities):
                    required_activity_fields = ["id", "name", "category", "description", "location", "address", "estimated_duration", "best_time"]
                    activity_missing_fields = [field for field in required_activity_fields if field not in activity]
                    
                    if activity_missing_fields:
                        print(f"❌ Activity {j+1} in Day {i} missing fields: {activity_missing_fields}")
                        return False
                    
                    # Check for solo female specific fields
                    if "solo_female_notes" in activity and activity["solo_female_notes"]:
                        print(f"  ✅ Solo female notes for {activity['name']}")
                    
                    if "safety_rating" in activity and activity["safety_rating"]:
                        print(f"  ✅ Safety rating for {activity['name']}: {activity['safety_rating']}")
                    
                    print(f"  - {activity['name']} ({activity['category']})")
            
            # Verify solo female interest is covered
            print(f"\n--- Solo Female Interest Coverage ---")
            all_categories = set()
            for day in days:
                for activity in day['activities']:
                    all_categories.add(activity['category'])
            
            if "solo female" in all_categories:
                print("✅ Solo female interest is covered in the itinerary")
            else:
                print("⚠️  Solo female interest not explicitly covered in activities")
            
            print(f"\n✅ Enhanced itinerary generation test passed!")
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced itinerary generation test failed with error: {e}")
        return False

def test_export_functionality():
    """Test the POST /api/export-itinerary endpoint"""
    print("\n" + "=" * 60)
    print("Testing Export Functionality")
    print("=" * 60)
    
    # Test export request
    test_data = {
        "itinerary_id": "test-itinerary-123",
        "format": "pdf"
    }
    
    try:
        url = f"{API_BASE}/export-itinerary"
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
            print("✅ Export functionality endpoint working!")
            
            # Validate response structure
            required_fields = ["status", "message", "export_id"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Response missing required fields: {missing_fields}")
                return False
            
            if data["status"] == "success":
                print(f"✅ Export status: {data['status']}")
                print(f"✅ Export message: {data['message']}")
                print(f"✅ Export ID: {data['export_id']}")
                return True
            else:
                print(f"❌ Export failed with status: {data['status']}")
                return False
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Export functionality test failed with error: {e}")
        return False

def main():
    """Run all enhanced backend API tests"""
    print("Starting Enhanced Backend API Tests for Dream Travels")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test 1: Enhanced Destinations Endpoint
    destinations_success = test_enhanced_destinations_endpoint()
    
    # Test 2: Enhanced Interests Endpoint
    interests_success = test_enhanced_interests_endpoint()
    
    # Test 3: Enhanced Itinerary Generation
    itinerary_success = test_enhanced_itinerary_generation()
    
    # Test 4: Export Functionality
    export_success = test_export_functionality()
    
    # Summary
    print("\n" + "=" * 60)
    print("ENHANCED TEST SUMMARY")
    print("=" * 60)
    print(f"Enhanced Destinations: {'✅ PASS' if destinations_success else '❌ FAIL'}")
    print(f"Enhanced Interests: {'✅ PASS' if interests_success else '❌ FAIL'}")
    print(f"Enhanced Itinerary Generation: {'✅ PASS' if itinerary_success else '❌ FAIL'}")
    print(f"Export Functionality: {'✅ PASS' if export_success else '❌ FAIL'}")
    
    all_passed = destinations_success and interests_success and itinerary_success and export_success
    
    if all_passed:
        print("\n🎉 All enhanced backend API tests passed!")
        return 0
    else:
        print("\n💥 Some enhanced backend API tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())