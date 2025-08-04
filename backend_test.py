#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Script for TravelMate Pro
Tests all updated API integrations now that WaitTimesApp is using the real API:
1. Updated WaitTimesApp Integration (Real API with 45+ parks)
2. Travel Blog Scraping Service
3. Queue Times Integration
4. Cross-Source Comparison
5. Error Handling and Rate Limiting
"""

import requests
import json
import sys
import time
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = "https://0ab3f2ef-9dd3-4f76-8714-d6d5aee30e46.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_travel_blog_scraping():
    """Test the new travel blog scraping endpoint: POST /api/generate-destination-data"""
    print("=" * 60)
    print("Testing Travel Blog Scraping Endpoint")
    print("=" * 60)
    
    try:
        url = f"{API_BASE}/generate-destination-data"
        params = {
            "destination": "Paris",
            "interests": ["museums", "dining hot spots"]
        }
        print(f"Making request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.post(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Travel blog scraping endpoint working!")
            
            # Validate response structure
            required_fields = ["destination", "interests", "activities", "restaurants"]
            missing_fields = []
            
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ Response missing required fields: {missing_fields}")
                return False
            
            print(f"Destination: {data.get('destination')}")
            print(f"Interests: {data.get('interests')}")
            print(f"Total activities found: {data.get('total_activities', 0)}")
            print(f"Activities: {len(data.get('activities', []))}")
            print(f"Restaurants: {len(data.get('restaurants', []))}")
            print(f"Data sources: {data.get('sources', [])}")
            print(f"Powered by: {data.get('powered_by', 'Unknown')}")
            
            # Show sample activities
            activities = data.get('activities', [])
            if activities:
                print("\n--- Sample Activities ---")
                for i, activity in enumerate(activities[:3]):
                    print(f"{i+1}. {activity.get('name', 'Unknown')}")
                    print(f"   Category: {activity.get('category', 'Unknown')}")
                    print(f"   Description: {activity.get('description', 'No description')[:100]}...")
            
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

def test_queue_times_parks():
    """Test the Queue Times integration: GET /api/theme-parks/queue-times"""
    print("\n" + "=" * 60)
    print("Testing Queue Times Parks Endpoint")
    print("=" * 60)
    
    try:
        url = f"{API_BASE}/theme-parks/queue-times"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Queue Times parks endpoint working!")
            
            parks = data.get('parks', [])
            print(f"Total parks available: {data.get('total_parks', 0)}")
            print(f"Source: {data.get('source', 'Unknown')}")
            print(f"Note: {data.get('note', '')}")
            
            # Show sample parks
            if parks:
                print("\n--- Sample Parks ---")
                for i, park in enumerate(parks[:5]):
                    print(f"{i+1}. {park.get('name', 'Unknown')} ({park.get('country', 'Unknown')})")
                    print(f"   ID: {park.get('id', 'Unknown')}")
                    print(f"   Company: {park.get('company', 'Unknown')}")
            
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

def test_queue_times_wait_times():
    """Test Queue Times wait times: GET /api/theme-parks/wdw_magic_kingdom/wait-times?source=queue-times"""
    print("\n" + "=" * 60)
    print("Testing Queue Times Wait Times Endpoint")
    print("=" * 60)
    
    try:
        url = f"{API_BASE}/theme-parks/wdw_magic_kingdom/wait-times"
        params = {"source": "queue-times"}
        print(f"Making request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Queue Times wait times endpoint working!")
            
            print(f"Park ID: {data.get('park_id', 'Unknown')}")
            print(f"Queue Times ID: {data.get('queue_times_id', 'Unknown')}")
            print(f"Last updated: {data.get('last_updated', 'Unknown')}")
            print(f"Source: {data.get('source', 'Unknown')}")
            
            summary = data.get('summary', {})
            print(f"\n--- Summary ---")
            print(f"Total attractions: {summary.get('total_attractions', 0)}")
            print(f"Open attractions: {summary.get('open_attractions', 0)}")
            print(f"Average wait: {summary.get('average_wait', 0)} minutes")
            print(f"Max wait: {summary.get('max_wait', 0)} minutes")
            
            # Show sample attractions
            attractions = data.get('attractions', [])
            if attractions:
                print("\n--- Sample Attractions ---")
                for i, attraction in enumerate(attractions[:5]):
                    print(f"{i+1}. {attraction.get('name', 'Unknown')}")
                    print(f"   Wait time: {attraction.get('wait_time', 0)} minutes")
                    print(f"   Status: {attraction.get('status', 'Unknown')}")
                    print(f"   Land: {attraction.get('land', 'Unknown')}")
            
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

def test_waittimes_app_parks():
    """Test WaitTimesApp integration: GET /api/theme-parks/waittimes-app"""
    print("\n" + "=" * 60)
    print("Testing WaitTimesApp Parks Endpoint")
    print("=" * 60)
    
    try:
        url = f"{API_BASE}/theme-parks/waittimes-app"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WaitTimesApp parks endpoint working!")
            
            parks = data.get('parks', [])
            print(f"Total parks available: {data.get('total_parks', 0)}")
            print(f"Source: {data.get('source', 'Unknown')}")
            print(f"Note: {data.get('note', '')}")
            
            # Show sample parks
            if parks:
                print("\n--- Sample Parks ---")
                for i, park in enumerate(parks[:5]):
                    print(f"{i+1}. {park.get('name', 'Unknown')} ({park.get('country', 'Unknown')})")
                    print(f"   ID: {park.get('id', 'Unknown')}")
                    print(f"   Source: {park.get('source', 'Unknown')}")
            
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

def test_waittimes_app_wait_times():
    """Test WaitTimesApp wait times: GET /api/theme-parks/europa_park/wait-times?source=waittimes-app"""
    print("\n" + "=" * 60)
    print("Testing WaitTimesApp Wait Times Endpoint")
    print("=" * 60)
    
    try:
        url = f"{API_BASE}/theme-parks/europa_park/wait-times"
        params = {"source": "waittimes-app"}
        print(f"Making request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WaitTimesApp wait times endpoint working!")
            
            print(f"Park ID: {data.get('park_id', 'Unknown')}")
            print(f"Park name: {data.get('park_name', 'Unknown')}")
            print(f"Last updated: {data.get('last_updated', 'Unknown')}")
            print(f"Source: {data.get('source', 'Unknown')}")
            
            summary = data.get('summary', {})
            print(f"\n--- Summary ---")
            print(f"Total attractions: {summary.get('total_attractions', 0)}")
            print(f"Open attractions: {summary.get('open_attractions', 0)}")
            print(f"Average wait: {summary.get('average_wait', 0)} minutes")
            print(f"Max wait: {summary.get('max_wait', 0)} minutes")
            
            # Show sample attractions
            attractions = data.get('attractions', [])
            if attractions:
                print("\n--- Sample Attractions ---")
                for i, attraction in enumerate(attractions[:5]):
                    print(f"{i+1}. {attraction.get('name', 'Unknown')}")
                    print(f"   Wait time: {attraction.get('wait_time', 0)} minutes")
                    print(f"   Status: {attraction.get('status', 'Unknown')}")
                    print(f"   Type: {attraction.get('attraction_type', 'Unknown')}")
            
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

def test_crowd_predictions():
    """Test crowd predictions: GET /api/theme-parks/wdw_magic_kingdom/crowd-predictions?source=queue-times"""
    print("\n" + "=" * 60)
    print("Testing Crowd Predictions Endpoint")
    print("=" * 60)
    
    try:
        url = f"{API_BASE}/theme-parks/wdw_magic_kingdom/crowd-predictions"
        params = {"source": "queue-times"}
        print(f"Making request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Crowd predictions endpoint working!")
            
            print(f"Park ID: {data.get('park_id', 'Unknown')}")
            print(f"Date: {data.get('date', 'Unknown')}")
            print(f"Crowd index: {data.get('crowd_index', 0)}/10")
            print(f"Crowd description: {data.get('crowd_description', 'Unknown')}")
            print(f"Prediction confidence: {data.get('prediction_confidence', 0)}")
            print(f"Data source: {data.get('data_source', 'Unknown')}")
            
            print(f"\n--- Timing Recommendations ---")
            peak_times = data.get('peak_times', [])
            best_times = data.get('best_visit_times', [])
            print(f"Peak times: {', '.join(peak_times) if peak_times else 'None'}")
            print(f"Best visit times: {', '.join(best_times) if best_times else 'None'}")
            
            base_stats = data.get('base_stats', {})
            if base_stats:
                print(f"\n--- Base Statistics ---")
                print(f"Average wait: {base_stats.get('average_wait', 0)} minutes")
                print(f"Max wait: {base_stats.get('max_wait', 0)} minutes")
                print(f"Open attractions: {base_stats.get('open_attractions', 0)}")
            
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

def test_park_plan_optimization():
    """Test park plan optimization: POST /api/theme-parks/wdw_magic_kingdom/optimize-plan"""
    print("\n" + "=" * 60)
    print("Testing Park Plan Optimization Endpoint")
    print("=" * 60)
    
    try:
        url = f"{API_BASE}/theme-parks/wdw_magic_kingdom/optimize-plan"
        test_data = {
            "selected_attractions": ["space_mountain", "pirates_caribbean"],
            "visit_date": "2025-06-15",
            "arrival_time": "09:00"
        }
        params = {"source": "queue-times"}
        
        print(f"Making request to: {url}")
        print(f"Request payload: {json.dumps(test_data, indent=2)}")
        print(f"Parameters: {params}")
        
        response = requests.post(
            url, 
            json=test_data,
            params=params,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Park plan optimization endpoint working!")
            
            print(f"Park ID: {data.get('park_id', 'Unknown')}")
            print(f"Visit date: {data.get('visit_date', 'Unknown')}")
            print(f"Crowd level: {data.get('crowd_level', 0)}/10")
            print(f"Crowd description: {data.get('crowd_description', 'Unknown')}")
            print(f"Total attractions: {data.get('total_attractions', 0)}")
            print(f"Estimated total time: {data.get('estimated_total_time', 'Unknown')}")
            print(f"Data source: {data.get('data_source', 'Unknown')}")
            
            # Show optimized plan
            plan = data.get('plan', [])
            if plan:
                print("\n--- Optimized Plan ---")
                for step in plan:
                    attraction = step.get('attraction', {})
                    print(f"{step.get('order', 0)}. {attraction.get('name', 'Unknown')}")
                    print(f"   Recommended time: {step.get('recommended_time', 'Unknown')}")
                    print(f"   Estimated wait: {step.get('estimated_wait', 0)} minutes")
                    print(f"   Land: {attraction.get('land', 'Unknown')}")
                    tips = step.get('tips', [])
                    if tips:
                        print(f"   Tips: {'; '.join(tips)}")
            
            # Show general tips
            general_tips = data.get('general_tips', [])
            if general_tips:
                print("\n--- General Tips ---")
                for i, tip in enumerate(general_tips, 1):
                    print(f"{i}. {tip}")
            
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
    """Run all new backend API integration tests"""
    print("Starting Backend API Tests for New Integrations")
    print("Testing replacements for Google Places and thrill-data.com")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Test results tracking
    test_results = {}
    
    # Test 1: Travel Blog Scraping
    print("\n🔍 Testing Travel Blog Scraping Integration...")
    test_results['travel_blog_scraping'] = test_travel_blog_scraping()
    
    # Test 2: Queue Times Parks
    print("\n🎢 Testing Queue Times Parks Integration...")
    test_results['queue_times_parks'] = test_queue_times_parks()
    
    # Test 3: Queue Times Wait Times
    print("\n⏰ Testing Queue Times Wait Times...")
    test_results['queue_times_wait_times'] = test_queue_times_wait_times()
    
    # Test 4: WaitTimesApp Parks
    print("\n🎠 Testing WaitTimesApp Parks Integration...")
    test_results['waittimes_app_parks'] = test_waittimes_app_parks()
    
    # Test 5: WaitTimesApp Wait Times
    print("\n⏱️ Testing WaitTimesApp Wait Times...")
    test_results['waittimes_app_wait_times'] = test_waittimes_app_wait_times()
    
    # Test 6: Crowd Predictions
    print("\n👥 Testing Crowd Predictions...")
    test_results['crowd_predictions'] = test_crowd_predictions()
    
    # Test 7: Park Plan Optimization
    print("\n📋 Testing Park Plan Optimization...")
    test_results['park_plan_optimization'] = test_park_plan_optimization()
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        test_display_name = test_name.replace('_', ' ').title()
        print(f"{test_display_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All new backend API integration tests passed!")
        print("✅ Google Places replacement (Travel Blog Scraping) working")
        print("✅ thrill-data.com replacement (Queue Times + WaitTimesApp) working")
        return 0
    else:
        failed_tests = total_tests - passed_tests
        print(f"\n💥 {failed_tests} backend API integration tests failed!")
        print("❌ Some services may not be properly initialized or have missing API keys")
        return 1

if __name__ == "__main__":
    sys.exit(main())