from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date
from destinations_database import (
    DESTINATIONS_DATABASE, 
    SOLO_FEMALE_SAFETY_GUIDELINES,
    get_destinations_by_region,
    get_solo_female_safe_destinations,
    get_hidden_gems,
    search_destinations_by_interest
)
from theme_park_service import ThemeParkService
from travel_blog_service import TravelBlogService
from queue_times_service import QueueTimesService
from waittimes_app_service import WaitTimesAppService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with fallback
try:
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        # Fallback for local development
        load_dotenv(ROOT_DIR / '.env')
        mongo_url = os.environ['MONGO_URL']
    
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.environ.get('DB_NAME', 'dream_travels_db')
    db = client[db_name]
    
    # Test the connection
    print(f"MongoDB connected to: {db_name}")
    
except Exception as e:
    print(f"MongoDB connection error: {e}")
    # Continue without database for now
    client = None
    db = None

# Initialize services with error handling
try:
    if client:
        theme_park_service = ThemeParkService(client)
        travel_blog_service = TravelBlogService(client) 
        queue_times_service = QueueTimesService(client)
        waittimes_app_service = WaitTimesAppService(client)
        print("All services initialized successfully")
    else:
        print("Warning: Services not initialized due to database connection issues")
        theme_park_service = None
        travel_blog_service = None
        queue_times_service = None
        waittimes_app_service = None
except Exception as e:
    print(f"Service initialization error: {e}")
    theme_park_service = None
    travel_blog_service = None
    queue_times_service = None
    waittimes_app_service = None

# Create the main app without a prefix
app = FastAPI(title="Dream Travels", description="Advanced Travel Itinerary Builder")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enhanced Models with Custom Activities
class CustomActivity(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    category: str = "custom"
    priority: int = Field(ge=1, le=5, default=3, description="Priority level 1-5")

class ItineraryRequest(BaseModel):
    destination: str
    interests: List[str]
    travel_dates: Optional[List[str]] = None
    number_of_days: Optional[int] = None
    budget_range: Optional[str] = None  # "budget", "mid-range", "luxury"
    solo_female_traveler: Optional[bool] = False
    max_distance_km: Optional[int] = None
    custom_activities: Optional[List[CustomActivity]] = []  # New field for custom activities
    
class Activity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    description: str = ""
    location: Dict[str, float] = {"lat": 0.0, "lng": 0.0}  # Default location
    address: str = ""
    estimated_duration: str = "2-3 hours"  # Default duration
    best_time: str = "Any time"
    image_url: Optional[str] = None
    solo_female_notes: Optional[str] = None
    safety_rating: Optional[int] = None
    is_custom: bool = False  # New field to identify custom activities

class DayItinerary(BaseModel):
    day: int
    date: Optional[str] = None
    activities: List[Activity]
    total_estimated_time: str
    safety_notes: Optional[str] = None

class Itinerary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    destination: str
    interests: List[str]
    days: List[DayItinerary]
    solo_female_safety_rating: Optional[int] = None
    safety_notes: Optional[str] = None
    custom_activities_included: int = 0  # Count of custom activities
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    preferences: Dict[str, Any] = {}
    saved_itineraries: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SavedItinerary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    destination: str
    interests: List[str]
    travel_dates: Optional[List[str]] = None
    number_of_days: Optional[int] = None
    itinerary: Itinerary
    is_public: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExportRequest(BaseModel):
    itinerary_id: str
    format: str = "pdf"  # "pdf", "email"
    email: Optional[str] = None

# Helper Functions
def calculate_distance(coord1: Dict[str, float], coord2: Dict[str, float]) -> float:
    """Simple distance calculation (approximate)"""
    lat_diff = coord1["lat"] - coord2["lat"]
    lng_diff = coord1["lng"] - coord2["lng"]
    return (lat_diff ** 2 + lng_diff ** 2) ** 0.5

def cluster_activities_by_location(activities: List[Activity], max_distance: float = 0.05) -> List[List[Activity]]:
    """Group activities by geographic proximity"""
    if not activities:
        return []
    
    clusters = []
    remaining = activities.copy()
    
    while remaining:
        current_cluster = [remaining.pop(0)]
        center = current_cluster[0].location
        
        i = 0
        while i < len(remaining):
            if calculate_distance(center, remaining[i].location) < max_distance:
                current_cluster.append(remaining.pop(i))
            else:
                i += 1
        
        clusters.append(current_cluster)
    
    return clusters

def normalize_destination_key(destination: str) -> str:
    """Normalize destination name for database lookup"""
    # Remove common suffixes and normalize
    dest_key = destination.lower()
    dest_key = dest_key.replace(" ", "_").replace(",", "").replace(".", "")
    
    # Handle common variations
    mappings = {
        "new_york_ny": "new_york",
        "new_york_city": "new_york", 
        "nyc": "new_york",
        "paris_france": "paris",
        "tokyo_japan": "tokyo",
        "mexico_city_mexico": "mexico_city",
        "buenos_aires_argentina": "buenos_aires",
        "toronto_ontario": "toronto",
        "toronto_canada": "toronto",
        "london_uk": "london",
        "london_england": "london"
    }
    
    return mappings.get(dest_key, dest_key)

def create_custom_activity_from_input(custom_activity: CustomActivity, destination_center: Dict[str, float]) -> Activity:
    """Convert custom activity input to Activity object"""
    # For custom activities, we'll place them near the destination center with some offset
    import random
    lat_offset = random.uniform(-0.01, 0.01)
    lng_offset = random.uniform(-0.01, 0.01)
    
    return Activity(
        name=custom_activity.name,
        category=custom_activity.category,
        description=custom_activity.description or f"Custom activity: {custom_activity.name}",
        location={
            "lat": destination_center["lat"] + lat_offset,
            "lng": destination_center["lng"] + lng_offset
        },
        address=custom_activity.location,
        estimated_duration="2-3 hours",
        best_time="Flexible",
        is_custom=True,
        solo_female_notes="Custom activity - please research safety independently"
    )

def get_destination_center(dest_key: str) -> Dict[str, float]:
    """Get approximate center coordinates for a destination"""
    centers = {
        "london": {"lat": 51.5074, "lng": -0.1278},
        "paris": {"lat": 48.8566, "lng": 2.3522},
        "new_york": {"lat": 40.7128, "lng": -74.0060},
        "tokyo": {"lat": 35.6762, "lng": 139.6503},
        "toronto": {"lat": 43.6532, "lng": -79.3832},
        "melbourne": {"lat": -37.8136, "lng": 144.9631}
    }
    return centers.get(dest_key, {"lat": 0.0, "lng": 0.0})

def create_enhanced_itinerary(
    destination: str, 
    interests: List[str], 
    num_days: int, 
    travel_dates: Optional[List[str]] = None,
    solo_female_traveler: bool = False,
    budget_range: Optional[str] = None,
    custom_activities: Optional[List[CustomActivity]] = None
) -> Itinerary:
    """Create enhanced itinerary with safety considerations and custom activities"""
    
    dest_key = normalize_destination_key(destination)
    
    if dest_key not in DESTINATIONS_DATABASE:
        # Try to find partial matches
        possible_matches = [k for k in DESTINATIONS_DATABASE.keys() if dest_key in k or k in dest_key]
        if possible_matches:
            dest_key = possible_matches[0]
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Destination '{destination}' not found. Available destinations: {list(DESTINATIONS_DATABASE.keys())}"
            )
    
    dest_data = DESTINATIONS_DATABASE[dest_key]
    
    # Add solo female interest if requested
    if solo_female_traveler and "solo female" not in interests:
        interests.append("solo female")
    
    # Collect activities based on interests
    selected_activities = []
    dest_activities = dest_data.get("activities", {})
    
    for interest in interests:
        interest_key = interest.lower()
        if interest_key in dest_activities:
            for activity_data in dest_activities[interest_key]:
                activity = Activity(**activity_data)
                selected_activities.append(activity)
    
    # Add custom activities
    custom_count = 0
    if custom_activities:
        destination_center = get_destination_center(dest_key)
        for custom_activity in custom_activities:
            custom_activity_obj = create_custom_activity_from_input(custom_activity, destination_center)
            selected_activities.append(custom_activity_obj)
            custom_count += 1
    
    if not selected_activities:
        raise HTTPException(
            status_code=400, 
            detail=f"No activities found for interests: {interests} in {destination}"
        )
    
    # Apply budget filtering (basic implementation)
    if budget_range:
        # This would be enhanced with real pricing data
        pass
    
    # Cluster activities by location
    activity_clusters = cluster_activities_by_location(selected_activities)
    
    # Distribute clusters across days
    days = []
    for day_num in range(1, num_days + 1):
        day_activities = []
        
        for i, cluster in enumerate(activity_clusters):
            if i % num_days == (day_num - 1):
                day_activities.extend(cluster)
        
        # Calculate total time for the day
        total_minutes = 0
        for act in day_activities:
            duration_str = act.estimated_duration.split('-')[0].split()[0]
            try:
                total_minutes += int(duration_str) * 60
            except:
                total_minutes += 120  # default 2 hours
        
        total_hours = total_minutes // 60
        total_time = f"{total_hours} hours" if total_hours > 0 else "Less than 1 hour"
        
        # Set date if provided
        day_date = None
        if travel_dates and len(travel_dates) >= day_num:
            day_date = travel_dates[day_num - 1]
        
        # Add safety notes for solo female travelers
        safety_notes = None
        if solo_female_traveler:
            safety_notes = f"Solo female safety rating for {destination}: {dest_data['solo_female_safety']}/5. {dest_data['safety_notes']}"
        
        days.append(DayItinerary(
            day=day_num,
            date=day_date,
            activities=day_activities,
            total_estimated_time=total_time,
            safety_notes=safety_notes
        ))
    
    return Itinerary(
        destination=destination,
        interests=interests,
        days=days,
        solo_female_safety_rating=dest_data.get('solo_female_safety'),
        safety_notes=dest_data.get('safety_notes') if solo_female_traveler else None,
        custom_activities_included=custom_count
    )

# Enhanced API Endpoints

@api_router.post("/generate-itinerary", response_model=Itinerary)
async def generate_enhanced_itinerary(request: ItineraryRequest):
    """Generate enhanced personalized itinerary with safety and budget considerations"""
    try:
        num_days = request.number_of_days or len(request.travel_dates or [])
        if not num_days:
            raise HTTPException(status_code=400, detail="Either number_of_days or travel_dates must be provided")
        
        itinerary = create_enhanced_itinerary(
            destination=request.destination,
            interests=request.interests,
            num_days=num_days,
            travel_dates=request.travel_dates,
            solo_female_traveler=request.solo_female_traveler,
            budget_range=request.budget_range,
            custom_activities=request.custom_activities
        )
        
        return itinerary
    except Exception as e:
        logger.error(f"Error generating itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/destinations", response_model=Dict[str, Any])
async def get_all_destinations(
    region: Optional[str] = Query(None, description="Filter by region"),
    city: Optional[str] = Query(None, description="Filter by specific city or area"),
    solo_female_safe: Optional[bool] = Query(False, description="Show only solo female safe destinations"),
    hidden_gems: Optional[bool] = Query(False, description="Show only hidden gems")
):
    """Get destinations with optional filtering - only shows destinations with safety rating 3+"""
    
    # Start with only safe destinations (safety rating >= 3)
    safe_destinations = {
        k: v for k, v in DESTINATIONS_DATABASE.items() 
        if v["solo_female_safety"] >= 3
    }
    
    destinations = safe_destinations.copy()
    
    if region:
        destinations = {k: v for k, v in destinations.items() if v["region"].lower() == region.lower()}
    
    if city:
        city_lower = city.lower()
        destinations = {
            k: v for k, v in destinations.items() 
            if city_lower in v["name"].lower() or city_lower in v["country"].lower()
        }
    
    if solo_female_safe:
        destinations = {k: v for k, v in destinations.items() if v["solo_female_safety"] >= 4}
    
    if hidden_gems:
        destinations = {k: v for k, v in destinations.items() if v.get("hidden_gem", False)}
    
    # Format for frontend consumption
    formatted_destinations = []
    for key, data in destinations.items():
        formatted_destinations.append({
            "key": key,
            "name": data["name"],
            "country": data["country"],
            "region": data["region"],
            "description": data["description"],
            "solo_female_safety": data["solo_female_safety"],
            "safety_notes": data["safety_notes"],
            "hidden_gem": data.get("hidden_gem", False)
        })
    
    return {
        "destinations": formatted_destinations,
        "total": len(formatted_destinations),
        "regions": list(set([d["region"] for d in formatted_destinations])),
        "cities": list(set([d["name"].split(",")[0] for d in formatted_destinations]))
    }

@api_router.get("/interests", response_model=Dict[str, Any])
async def get_available_interests():
    """Get all available interest categories including solo female"""
    interests = [
        "scenic drives",
        "hikes", 
        "beaches",
        "theme parks",
        "museums",
        "historic landmarks", 
        "family friendly",
        "dining hot spots",
        "outdoor activities",
        "cultural experiences",
        "nightlife",
        "shopping",
        "solo female"  # New category
    ]
    
    return {
        "interests": interests,
        "solo_female_guidelines": SOLO_FEMALE_SAFETY_GUIDELINES
    }

@api_router.get("/cities-and-regions")
async def get_cities_and_regions():
    """Get organized list of cities and regions for filtering"""
    safe_destinations = {
        k: v for k, v in DESTINATIONS_DATABASE.items() 
        if v["solo_female_safety"] >= 3
    }
    
    regions = {}
    cities = []
    
    for key, data in safe_destinations.items():
        region = data["region"]
        if region not in regions:
            regions[region] = []
        
        city_info = {
            "key": key,
            "name": data["name"],
            "country": data["country"],
            "safety_rating": data["solo_female_safety"],
            "hidden_gem": data.get("hidden_gem", False)
        }
        
        regions[region].append(city_info)
        cities.append(city_info)
    
    return {
        "regions": regions,
        "all_cities": sorted(cities, key=lambda x: x["name"]),
        "popular_cities": [
            city for city in cities 
            if city["safety_rating"] >= 4 and not city["hidden_gem"]
        ][:10]
    }

@api_router.get("/destinations/search")
async def search_destinations(
    interest: Optional[str] = Query(None, description="Search by interest"),
    city_name: Optional[str] = Query(None, description="Search by city name"),
    region: Optional[str] = Query(None, description="Filter by region")
):
    """Search destinations by various criteria - only safe destinations (3+ rating)"""
    
    # Start with safe destinations only
    results = {
        k: v for k, v in DESTINATIONS_DATABASE.items() 
        if v["solo_female_safety"] >= 3
    }
    
    if interest:
        results = search_destinations_by_interest(interest)
        # Re-filter for safety
        results = {k: v for k, v in results.items() if v["solo_female_safety"] >= 3}
    
    if city_name:
        city_lower = city_name.lower()
        results = {
            k: v for k, v in results.items() 
            if city_lower in v["name"].lower()
        }
    
    if region:
        results = {k: v for k, v in results.items() if v["region"].lower() == region.lower()}
    
    return {"destinations": results, "count": len(results)}

@api_router.post("/save-itinerary", response_model=SavedItinerary)
async def save_itinerary_enhanced(
    destination: str,
    interests: List[str], 
    itinerary: Itinerary,
    user_id: Optional[str] = None,
    is_public: bool = False
):
    """Save itinerary with user association"""
    saved = SavedItinerary(
        user_id=user_id,
        destination=destination,
        interests=interests,
        itinerary=itinerary,
        is_public=is_public
    )
    
    await db.itineraries.insert_one(saved.dict())
    return saved

@api_router.get("/saved-itineraries")
async def get_saved_itineraries(user_id: Optional[str] = Query(None)):
    """Get saved itineraries, optionally filtered by user"""
    query = {}
    if user_id:
        query["user_id"] = user_id
    else:
        query["is_public"] = True
    
    itineraries = await db.itineraries.find(query).to_list(100)
    return {"itineraries": itineraries}

@api_router.post("/export-itinerary")
async def export_itinerary(request: ExportRequest):
    """Export itinerary in various formats"""
    # This would integrate with PDF generation or email services
    return {
        "status": "success",
        "message": f"Itinerary export in {request.format} format requested",
        "export_id": str(uuid.uuid4())
    }

@api_router.post("/generate-destination-data")
async def generate_destination_data(
    destination: str = Query(..., description="Destination name"),
    interests: List[str] = Query(..., description="List of interests")
):
    """Generate destination data using travel blog scraping (replaces Google Places API)"""
    try:
        logger.info(f"Generating destination data for {destination} with interests: {interests}")
        
        # Use travel blog service to scrape destination information
        destination_data = await travel_blog_service.scrape_destination_data(destination, interests)
        
        if not destination_data:
            return {
                "error": "No data found for this destination",
                "destination": destination,
                "suggestions": "Try a more specific location name or check spelling"
            }
        
        # Transform the scraped data into activities compatible with our itinerary system
        activities = []
        
        # Process scraped activities
        for activity_data in destination_data.get("activities", []):
            # Ensure we have valid duration
            duration = activity_data.get("duration")
            if not duration or duration is None:
                duration = "2-3 hours"
            
            activity = Activity(
                name=activity_data.get("name", "Unknown Activity"),
                category=activity_data.get("category", "general"),
                description=activity_data.get("description", "")[:200] if activity_data.get("description") else "",
                location={"lat": 0.0, "lng": 0.0},  # Would need geocoding for exact coordinates
                address=f"{destination}",  # Generic address
                estimated_duration=duration,
                best_time="Morning or afternoon",
                is_custom=False
            )
            activities.append(activity)
        
        # Process restaurants as dining activities
        for restaurant_data in destination_data.get("restaurants", []):
            activity = Activity(
                name=restaurant_data.get("name", "Local Restaurant"),
                category="dining hot spots",
                description=restaurant_data.get("description", ""),
                location={"lat": 0.0, "lng": 0.0},
                address=f"{destination}",
                estimated_duration="1-2 hours",
                best_time="Lunch or dinner time",
                is_custom=False
            )
            activities.append(activity)
        
        return {
            "destination": destination,
            "interests": interests,
            "total_activities": len(activities),
            "activities": [activity.dict() for activity in activities[:20]],  # Limit to 20
            "restaurants": destination_data.get("restaurants", [])[:10],  # Limit to 10
            "accommodations": destination_data.get("accommodations", [])[:5],  # Limit to 5
            "local_tips": destination_data.get("local_tips", [])[:8],  # Limit to 8
            "budget_info": destination_data.get("budget_info", {}),
            "safety_info": destination_data.get("safety_info", {}),
            "sources": destination_data.get("sources", []),
            "data_freshness": destination_data.get("last_updated"),
            "powered_by": "Travel Blog Scraping Service"
        }
        
    except Exception as e:
        logger.error(f"Error generating destination data: {e}")
        return {
            "error": f"Failed to generate destination data: {str(e)}",
            "destination": destination
        }

@api_router.get("/theme-parks/queue-times")
async def get_theme_parks_queue_times():
    """Get available theme parks from Queue Times API"""
    try:
        parks = await queue_times_service.get_available_parks()
        return {
            "parks": parks,
            "total_parks": len(parks),
            "source": "queue-times.com",
            "note": "Free API with 80+ theme parks worldwide"
        }
    except Exception as e:
        logger.error(f"Error fetching Queue Times parks: {e}")
        return {"error": f"Failed to fetch parks: {str(e)}"}

@api_router.get("/theme-parks/waittimes-app")
async def get_theme_parks_waittimes_app():
    """Get available theme parks from WaitTimesApp API"""
    try:
        parks = await waittimes_app_service.get_available_parks()
        return {
            "parks": parks,
            "total_parks": len(parks),
            "source": "waittimes-app",
            "note": "International theme park coverage"
        }
    except Exception as e:
        logger.error(f"Error fetching WaitTimesApp parks: {e}")
        return {"error": f"Failed to fetch parks: {str(e)}"}

@api_router.get("/theme-parks/{park_id}/wait-times")
async def get_park_wait_times(
    park_id: str,
    source: str = Query("queue-times", description="Data source: queue-times or waittimes-app")
):
    """Get real-time wait times for a specific theme park"""
    try:
        if source == "queue-times":
            wait_data = await queue_times_service.get_live_wait_times(park_id)
        elif source == "waittimes-app":
            wait_data = await waittimes_app_service.get_live_wait_times(park_id)
        else:
            return {"error": "Invalid source. Use 'queue-times' or 'waittimes-app'"}
        
        if not wait_data:
            return {"error": f"No wait time data found for park {park_id}"}
        
        return wait_data
        
    except Exception as e:
        logger.error(f"Error fetching wait times for {park_id}: {e}")
        return {"error": f"Failed to fetch wait times: {str(e)}"}

@api_router.get("/theme-parks/{park_id}/crowd-predictions")
async def get_park_crowd_predictions(
    park_id: str,
    date: str = Query(None, description="Target date (YYYY-MM-DD), defaults to today"),
    source: str = Query("queue-times", description="Data source: queue-times or waittimes-app")
):
    """Get crowd level predictions for a theme park"""
    try:
        from datetime import date as date_obj
        target_date = date_obj.today() if not date else date_obj.fromisoformat(date)
        
        if source == "queue-times":
            crowd_data = await queue_times_service.get_crowd_predictions(park_id, target_date)
        elif source == "waittimes-app":
            crowd_data = await waittimes_app_service.get_crowd_predictions(park_id, target_date)
        else:
            return {"error": "Invalid source. Use 'queue-times' or 'waittimes-app'"}
        
        if not crowd_data:
            return {"error": f"No crowd prediction data found for park {park_id}"}
        
        return crowd_data
        
    except Exception as e:
        logger.error(f"Error fetching crowd predictions for {park_id}: {e}")
        return {"error": f"Failed to fetch crowd predictions: {str(e)}"}

@api_router.post("/theme-parks/{park_id}/optimize-plan")
async def optimize_theme_park_plan(
    park_id: str,
    request: Dict[str, Any],
    source: str = Query("queue-times", description="Data source: queue-times or waittimes-app")
):
    """Generate optimized theme park touring plan"""
    try:
        selected_attractions = request.get("selected_attractions", [])
        visit_date_str = request.get("visit_date")
        arrival_time = request.get("arrival_time", "09:00")
        
        if not selected_attractions:
            return {"error": "No attractions selected"}
        
        from datetime import date as date_obj
        visit_date = date_obj.fromisoformat(visit_date_str) if visit_date_str else date_obj.today()
        
        if source == "queue-times":
            plan = await queue_times_service.optimize_park_plan(
                park_id, selected_attractions, visit_date, arrival_time
            )
        elif source == "waittimes-app":
            plan = await waittimes_app_service.optimize_park_plan(
                park_id, selected_attractions, visit_date, arrival_time
            )
        else:
            return {"error": "Invalid source. Use 'queue-times' or 'waittimes-app'"}
        
        if not plan:
            return {"error": "Failed to generate optimized plan"}
        
        return plan
        
    except Exception as e:
        logger.error(f"Error optimizing theme park plan: {e}")
        return {"error": f"Failed to optimize plan: {str(e)}"}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected" if client else "disconnected",
            "theme_parks": "initialized" if theme_park_service else "not initialized",
            "travel_blogs": "initialized" if travel_blog_service else "not initialized"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Dream Travels API is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "destinations": "/api/destinations",
            "interests": "/api/interests",
            "theme_parks": "/api/theme-parks/queue-times"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)