from fastapi import FastAPI, APIRouter, HTTPException
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
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class ItineraryRequest(BaseModel):
    destination: str
    interests: List[str]
    travel_dates: Optional[List[str]] = None
    number_of_days: Optional[int] = None
    
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

class DayItinerary(BaseModel):
    day: int
    date: Optional[str] = None
    activities: List[Activity]
    total_estimated_time: str

class Itinerary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    destination: str
    interests: List[str]
    days: List[DayItinerary]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SavedItinerary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    destination: str
    interests: List[str]
    travel_dates: Optional[List[str]] = None
    number_of_days: Optional[int] = None
    itinerary: Itinerary
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Mock activity data organized by categories and locations
MOCK_ACTIVITIES = {
    "orlando": {
        "theme parks": [
            Activity(name="Magic Kingdom", category="theme parks", description="Disney's flagship theme park with classic attractions and characters", location={"lat": 28.3852, "lng": -81.5639}, address="1180 Seven Seas Dr, Bay Lake, FL 32830", estimated_duration="8-10 hours", best_time="8:00 AM - Park Close", image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945"),
            Activity(name="Universal Studios", category="theme parks", description="Movie-themed attractions and thrilling rides", location={"lat": 28.4794, "lng": -81.4685}, address="6000 Universal Blvd, Orlando, FL 32819", estimated_duration="8-10 hours", best_time="9:00 AM - Park Close"),
            Activity(name="EPCOT", category="theme parks", description="Disney's experimental prototype community with world showcase", location={"lat": 28.3747, "lng": -81.5494}, address="200 Epcot Center Dr, Bay Lake, FL 32830", estimated_duration="8-10 hours", best_time="9:00 AM - Park Close"),
        ],
        "family friendly": [
            Activity(name="Gatorland", category="family friendly", description="Alligator theme park with shows and exhibits", location={"lat": 28.3553, "lng": -81.4024}, address="14501 S Orange Blossom Trl, Orlando, FL 32837", estimated_duration="3-4 hours", best_time="10:00 AM - 4:00 PM"),
            Activity(name="Icon Park", category="family friendly", description="Entertainment complex with observation wheel and attractions", location={"lat": 28.4432, "lng": -81.4685}, address="8401 International Dr, Orlando, FL 32819", estimated_duration="2-3 hours", best_time="5:00 PM - 9:00 PM"),
        ],
        "dining hot spots": [
            Activity(name="Disney Springs", category="dining hot spots", description="Outdoor shopping and dining district", location={"lat": 28.3720, "lng": -81.5158}, address="1486 Buena Vista Dr, Lake Buena Vista, FL 32830", estimated_duration="2-3 hours", best_time="6:00 PM - 10:00 PM"),
            Activity(name="International Drive", category="dining hot spots", description="Tourist corridor with diverse restaurants", location={"lat": 28.4432, "lng": -81.4685}, address="International Dr, Orlando, FL", estimated_duration="1-2 hours", best_time="7:00 PM - 9:00 PM"),
        ]
    },
    "san francisco": {
        "scenic drives": [
            Activity(name="Golden Gate Bridge Drive", category="scenic drives", description="Iconic drive across the Golden Gate Bridge with stunning views", location={"lat": 37.8199, "lng": -122.4783}, address="Golden Gate Bridge, San Francisco, CA", estimated_duration="1-2 hours", best_time="Morning for best lighting"),
            Activity(name="Lombard Street", category="scenic drives", description="The world's crookedest street with beautiful gardens", location={"lat": 37.8021, "lng": -122.4187}, address="Lombard St, San Francisco, CA 94133", estimated_duration="30 minutes", best_time="Mid-morning"),
        ],
        "historic landmarks": [
            Activity(name="Alcatraz Island", category="historic landmarks", description="Former federal prison on an island in San Francisco Bay", location={"lat": 37.8267, "lng": -122.4233}, address="Alcatraz Island, San Francisco, CA 94133", estimated_duration="3-4 hours", best_time="Morning tour"),
            Activity(name="Golden Gate Park", category="historic landmarks", description="Large urban park with museums and gardens", location={"lat": 37.7694, "lng": -122.4862}, address="Golden Gate Park, San Francisco, CA", estimated_duration="3-4 hours", best_time="10:00 AM - 4:00 PM"),
        ],
        "dining hot spots": [
            Activity(name="Fisherman's Wharf", category="dining hot spots", description="Waterfront area known for seafood and sourdough bread", location={"lat": 37.8081, "lng": -122.4156}, address="Fisherman's Wharf, San Francisco, CA", estimated_duration="2-3 hours", best_time="Lunch or dinner"),
            Activity(name="Union Square", category="dining hot spots", description="Shopping and dining district in downtown SF", location={"lat": 37.7880, "lng": -122.4074}, address="Union Square, San Francisco, CA", estimated_duration="2-3 hours", best_time="Afternoon to evening"),
        ]
    },
    "new york": {
        "museums": [
            Activity(name="Metropolitan Museum of Art", category="museums", description="One of the world's largest and most prestigious art museums", location={"lat": 40.7794, "lng": -73.9632}, address="1000 5th Ave, New York, NY 10028", estimated_duration="3-4 hours", best_time="10:00 AM - 2:00 PM"),
            Activity(name="Museum of Modern Art", category="museums", description="Premier collection of contemporary and modern art", location={"lat": 40.7614, "lng": -73.9776}, address="11 W 53rd St, New York, NY 10019", estimated_duration="2-3 hours", best_time="11:00 AM - 3:00 PM"),
        ],
        "historic landmarks": [
            Activity(name="Statue of Liberty", category="historic landmarks", description="Iconic symbol of freedom and democracy", location={"lat": 40.6892, "lng": -74.0445}, address="Liberty Island, New York, NY 10004", estimated_duration="4-5 hours", best_time="Morning ferry"),
            Activity(name="Empire State Building", category="historic landmarks", description="Art Deco skyscraper with observation decks", location={"lat": 40.7484, "lng": -73.9857}, address="20 W 34th St, New York, NY 10001", estimated_duration="2-3 hours", best_time="Sunset viewing"),
        ],
        "family friendly": [
            Activity(name="Central Park", category="family friendly", description="Large public park with playgrounds, lakes, and activities", location={"lat": 40.7829, "lng": -73.9654}, address="Central Park, New York, NY", estimated_duration="3-4 hours", best_time="Morning to afternoon"),
            Activity(name="Brooklyn Bridge", category="family friendly", description="Historic suspension bridge with pedestrian walkway", location={"lat": 40.7061, "lng": -73.9969}, address="Brooklyn Bridge, New York, NY", estimated_duration="1-2 hours", best_time="Morning or late afternoon"),
        ]
    }
}

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
        # Start a new cluster with the first remaining activity
        current_cluster = [remaining.pop(0)]
        center = current_cluster[0].location
        
        # Find nearby activities
        i = 0
        while i < len(remaining):
            if calculate_distance(center, remaining[i].location) < max_distance:
                current_cluster.append(remaining.pop(i))
            else:
                i += 1
        
        clusters.append(current_cluster)
    
    return clusters

def create_itinerary(destination: str, interests: List[str], num_days: int, travel_dates: Optional[List[str]] = None) -> Itinerary:
    """Create a smart itinerary based on interests and geographic clustering"""
    # Get destination key
    dest_key = destination.lower().replace(" ", "").replace(",", "")
    
    # Find matching destination in mock data
    if dest_key not in MOCK_ACTIVITIES:
        # Fallback to a generic set or throw error
        raise HTTPException(status_code=404, detail=f"Destination '{destination}' not supported yet. Try Orlando, San Francisco, or New York")
    
    # Collect activities based on interests
    selected_activities = []
    dest_activities = MOCK_ACTIVITIES[dest_key]
    
    for interest in interests:
        if interest.lower() in dest_activities:
            selected_activities.extend(dest_activities[interest.lower()])
    
    if not selected_activities:
        raise HTTPException(status_code=400, detail="No activities found for selected interests")
    
    # Cluster activities by location
    activity_clusters = cluster_activities_by_location(selected_activities)
    
    # Distribute clusters across days
    days = []
    for day_num in range(1, num_days + 1):
        day_activities = []
        
        # Assign clusters to days (round-robin style)
        for i, cluster in enumerate(activity_clusters):
            if i % num_days == (day_num - 1):
                day_activities.extend(cluster)
        
        # Calculate total time for the day
        total_minutes = sum([int(act.estimated_duration.split('-')[0].split()[0]) * 60 for act in day_activities])
        total_hours = total_minutes // 60
        total_time = f"{total_hours} hours" if total_hours > 0 else "Less than 1 hour"
        
        # Set date if provided
        day_date = None
        if travel_dates and len(travel_dates) >= day_num:
            day_date = travel_dates[day_num - 1]
        
        days.append(DayItinerary(
            day=day_num,
            date=day_date,
            activities=day_activities,
            total_estimated_time=total_time
        ))
    
    return Itinerary(
        destination=destination,
        interests=interests,
        days=days
    )

@api_router.post("/generate-itinerary", response_model=Itinerary)
async def generate_itinerary(request: ItineraryRequest):
    """Generate a personalized itinerary based on interests and location clustering"""
    try:
        num_days = request.number_of_days or len(request.travel_dates or [])
        if not num_days:
            raise HTTPException(status_code=400, detail="Either number_of_days or travel_dates must be provided")
        
        itinerary = create_itinerary(
            destination=request.destination,
            interests=request.interests,
            num_days=num_days,
            travel_dates=request.travel_dates
        )
        
        return itinerary
    except Exception as e:
        logger.error(f"Error generating itinerary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/save-itinerary", response_model=SavedItinerary)
async def save_itinerary(request: ItineraryRequest, itinerary: Itinerary):
    """Save a generated itinerary to the database"""
    saved = SavedItinerary(
        destination=request.destination,
        interests=request.interests,
        travel_dates=request.travel_dates,
        number_of_days=request.number_of_days,
        itinerary=itinerary
    )
    
    await db.itineraries.insert_one(saved.dict())
    return saved

@api_router.get("/saved-itineraries", response_model=List[SavedItinerary])
async def get_saved_itineraries():
    """Get all saved itineraries"""
    itineraries = await db.itineraries.find().to_list(100)
    return [SavedItinerary(**itinerary) for itinerary in itineraries]

@api_router.get("/available-destinations")
async def get_available_destinations():
    """Get list of available destinations"""
    return {
        "destinations": [
            {"name": "Orlando, FL", "key": "orlando", "description": "Theme parks and family attractions"},
            {"name": "San Francisco, CA", "key": "san francisco", "description": "Scenic drives and historic landmarks"},
            {"name": "New York, NY", "key": "new york", "description": "Museums and cultural attractions"}
        ]
    }

@api_router.get("/available-interests")
async def get_available_interests():
    """Get list of available interest categories"""
    return {
        "interests": [
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
            "shopping"
        ]
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