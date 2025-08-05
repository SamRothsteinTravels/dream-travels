"""
Optimized FastAPI server for Render deployment
Faster startup with minimal dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import json
from typing import List, Dict, Any
import asyncio
import httpx

# Create FastAPI app
app = FastAPI(
    title="Dream Travels API",
    description="Optimized travel planning API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Minimal destinations data (expandable)
DESTINATIONS = {
    "paris": {
        "name": "Paris, France",
        "description": "City of Light with world-class museums and dining",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe"
    },
    "london": {
        "name": "London, UK", 
        "description": "Historic capital with royal palaces and museums",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe"
    },
    "tokyo": {
        "name": "Tokyo, Japan",
        "description": "Modern metropolis blending tradition and innovation",
        "safety_rating": 5,
        "solo_female_rating": 5,
        "continent": "Asia"
    },
    "new_york": {
        "name": "New York, NY",
        "description": "The city that never sleeps with endless attractions",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "North America"  
    },
    "rome": {
        "name": "Rome, Italy",
        "description": "Eternal city with ancient history and amazing food",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "Europe"
    },
    "sydney": {
        "name": "Sydney, Australia",
        "description": "Harbor city with iconic opera house and beaches",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Australia"
    },
    "barcelona": {
        "name": "Barcelona, Spain", 
        "description": "Vibrant city with Gaudi architecture and Mediterranean coast",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "Europe"
    },
    "amsterdam": {
        "name": "Amsterdam, Netherlands",
        "description": "Canal city with rich history and liberal culture",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe"
    },
    "istanbul": {
        "name": "Istanbul, Turkey",
        "description": "Bridge between Europe and Asia with rich Ottoman history",
        "safety_rating": 3,
        "solo_female_rating": 2,
        "continent": "Asia"
    },
    "bali": {
        "name": "Bali, Indonesia",
        "description": "Tropical paradise with temples, beaches, and culture",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "Asia"
    }
}

# Sample activities for each destination
SAMPLE_ACTIVITIES = {
    "paris": [
        {"name": "Louvre Museum", "category": "museums", "duration": "3-4 hours"},
        {"name": "Eiffel Tower", "category": "historic landmarks", "duration": "2 hours"},
        {"name": "Notre-Dame Cathedral", "category": "historic landmarks", "duration": "1 hour"},
        {"name": "Champs-Élysées Shopping", "category": "dining hot spots", "duration": "2-3 hours"},
        {"name": "Seine River Cruise", "category": "scenic drives", "duration": "1.5 hours"}
    ],
    "london": [
        {"name": "British Museum", "category": "museums", "duration": "3-4 hours"},
        {"name": "Tower of London", "category": "historic landmarks", "duration": "2-3 hours"},
        {"name": "Westminster Abbey", "category": "historic landmarks", "duration": "1.5 hours"},
        {"name": "Borough Market", "category": "dining hot spots", "duration": "1-2 hours"},
        {"name": "Thames River Walk", "category": "scenic drives", "duration": "2 hours"}
    ],
    "tokyo": [
        {"name": "Senso-ji Temple", "category": "historic landmarks", "duration": "2 hours"},
        {"name": "Tokyo National Museum", "category": "museums", "duration": "3 hours"},
        {"name": "Tsukiji Outer Market", "category": "dining hot spots", "duration": "2 hours"},
        {"name": "Imperial Palace Gardens", "category": "outdoor", "duration": "1.5 hours"},
        {"name": "Shibuya Crossing", "category": "family friendly", "duration": "1 hour"}
    ]
}

# HTTP client for external APIs
http_client = httpx.AsyncClient(timeout=30.0)

@app.get("/")
async def root():
    return {
        "message": "Dream Travels API - Optimized Version",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "destinations": "/api/destinations", 
            "interests": "/api/interests",
            "theme_parks": "/api/theme-parks/queue-times"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Dream Travels API is running"
    }

@app.get("/api/destinations")
async def get_destinations():
    return {
        "destinations": DESTINATIONS,
        "count": len(DESTINATIONS),
        "message": "Available destinations for travel planning"
    }

@app.get("/api/interests")
async def get_interests():
    interests = [
        "scenic drives", "hikes", "beaches", "theme parks", "museums",
        "historic landmarks", "family friendly", "dining hot spots", 
        "outdoor", "solo female"
    ]
    return {
        "interests": interests,
        "solo_female_notes": "Destinations with safety ratings 3+ recommended for solo female travelers"
    }

@app.post("/api/generate-itinerary") 
async def generate_itinerary(request: dict):
    destination = request.get("destination", "").lower().replace(" ", "_").replace(",", "")
    interests = request.get("interests", [])
    number_of_days = request.get("number_of_days", 3)
    
    # Find destination
    dest_key = None
    for key in DESTINATIONS.keys():
        if destination in key or key in destination:
            dest_key = key
            break
    
    if not dest_key:
        return {"error": f"Destination not found. Available: {list(DESTINATIONS.keys())}"}
    
    # Get activities for destination
    activities = SAMPLE_ACTIVITIES.get(dest_key, [])
    
    # Filter by interests
    filtered_activities = []
    for activity in activities:
        if any(interest.lower() in activity["category"].lower() for interest in interests):
            filtered_activities.append({
                "id": f"{dest_key}_{activity['name'].replace(' ', '_').lower()}",
                "name": activity["name"],
                "category": activity["category"],
                "description": f"Experience {activity['name']} in {DESTINATIONS[dest_key]['name']}",
                "estimated_duration": activity["duration"],
                "best_time": "Morning or afternoon",
                "location": {"lat": 0.0, "lng": 0.0},
                "address": DESTINATIONS[dest_key]['name']
            })
    
    # Create day-by-day itinerary
    days = []
    activities_per_day = max(1, len(filtered_activities) // number_of_days)
    
    for day in range(1, number_of_days + 1):
        start_idx = (day - 1) * activities_per_day
        end_idx = start_idx + activities_per_day
        day_activities = filtered_activities[start_idx:end_idx]
        
        days.append({
            "day": day,
            "title": f"Day {day} in {DESTINATIONS[dest_key]['name']}",
            "activities": day_activities
        })
    
    return {
        "id": f"itinerary_{dest_key}_{datetime.utcnow().strftime('%Y%m%d')}",
        "destination": DESTINATIONS[dest_key]['name'],
        "interests": interests,
        "number_of_days": number_of_days,
        "days": days,
        "total_activities": len(filtered_activities),
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/api/theme-parks/queue-times")
async def get_theme_parks():
    try:
        # Try to get real data from Queue Times API
        response = await http_client.get("https://queue-times.com/parks.json")
        if response.status_code == 200:
            parks_data = response.json()
            parks = []
            for company in parks_data[:5]:  # Limit to prevent timeout
                company_parks = company.get("parks", [])[:10]  # Limit parks per company
                for park in company_parks:
                    parks.append({
                        "id": str(park.get("id", "")),
                        "name": park.get("name", "Unknown Park"),
                        "country": park.get("country", ""),
                        "source": "queue-times"
                    })
            
            return {
                "parks": parks,
                "total_parks": len(parks),
                "source": "queue-times.com",
                "message": "Live theme park data"
            }
    except Exception as e:
        pass
    
    # Fallback data
    return {
        "parks": [
            {"id": "6", "name": "Magic Kingdom", "country": "United States", "source": "queue-times"},
            {"id": "7", "name": "Disney's Hollywood Studios", "country": "United States", "source": "queue-times"},
            {"id": "8", "name": "EPCOT", "country": "United States", "source": "queue-times"}
        ],
        "total_parks": 3,
        "source": "fallback-data",
        "message": "Limited theme park data available"
    }

@app.get("/api/theme-parks/{park_id}/wait-times")
async def get_park_wait_times(park_id: str):
    try:
        # Try to get real wait times
        response = await http_client.get(f"https://queue-times.com/parks/{park_id}/queue_times.json")
        if response.status_code == 200:
            data = response.json()
            attractions = []
            
            for land in data.get("lands", [])[:3]:  # Limit lands
                for ride in land.get("rides", [])[:5]:  # Limit rides per land
                    attractions.append({
                        "id": str(ride.get("id", "")),
                        "name": ride.get("name", "Unknown Ride"),
                        "wait_time": ride.get("wait_time", 0),
                        "is_open": ride.get("is_open", False),
                        "land": land.get("name", "Unknown Land")
                    })
            
            return {
                "park_id": park_id,
                "attractions": attractions,
                "total_attractions": len(attractions),
                "source": "queue-times-live"
            }
    except Exception as e:
        pass
    
    # Fallback data
    return {
        "park_id": park_id,
        "attractions": [
            {"id": "1", "name": "Space Mountain", "wait_time": 45, "is_open": True, "land": "Tomorrowland"},
            {"id": "2", "name": "Pirates of the Caribbean", "wait_time": 20, "is_open": True, "land": "Adventureland"},
            {"id": "3", "name": "Haunted Mansion", "wait_time": 35, "is_open": True, "land": "Liberty Square"}
        ],
        "total_attractions": 3,
        "source": "fallback-data"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)