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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="TravelMate Pro", description="Advanced Travel Itinerary Builder")

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
    description: str
    location: Dict[str, float]  # {"lat": float, "lng": float}
    address: str
    estimated_duration: str
    best_time: str
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
        "toronto_canada": "toronto"
    }
    
    return mappings.get(dest_key, dest_key)

def create_enhanced_itinerary(
    destination: str, 
    interests: List[str], 
    num_days: int, 
    travel_dates: Optional[List[str]] = None,
    solo_female_traveler: bool = False,
    budget_range: Optional[str] = None
) -> Itinerary:
    """Create enhanced itinerary with safety considerations"""
    
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
        safety_notes=dest_data.get('safety_notes') if solo_female_traveler else None
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
            budget_range=request.budget_range
        )
        
        return itinerary
    except Exception as e:
        logger.error(f"Error generating itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/destinations", response_model=Dict[str, Any])
async def get_all_destinations(
    region: Optional[str] = Query(None, description="Filter by region"),
    solo_female_safe: Optional[bool] = Query(False, description="Show only solo female safe destinations"),
    hidden_gems: Optional[bool] = Query(False, description="Show only hidden gems"),
    min_safety_rating: Optional[int] = Query(None, description="Minimum solo female safety rating")
):
    """Get destinations with optional filtering"""
    
    destinations = DESTINATIONS_DATABASE.copy()
    
    if region:
        destinations = get_destinations_by_region(region)
    
    if solo_female_safe or min_safety_rating:
        rating = min_safety_rating or 4
        destinations = {k: v for k, v in destinations.items() if v["solo_female_safety"] >= rating}
    
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
        "regions": list(set([d["region"] for d in formatted_destinations]))
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

@api_router.get("/destinations/search")
async def search_destinations(
    interest: Optional[str] = Query(None, description="Search by interest"),
    safety_rating: Optional[int] = Query(None, description="Minimum safety rating"),
    region: Optional[str] = Query(None, description="Filter by region")
):
    """Search destinations by various criteria"""
    
    results = DESTINATIONS_DATABASE.copy()
    
    if interest:
        results = search_destinations_by_interest(interest)
    
    if safety_rating:
        results = {k: v for k, v in results.items() if v["solo_female_safety"] >= safety_rating}
    
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
    return {"status": "healthy", "timestamp": datetime.utcnow()}