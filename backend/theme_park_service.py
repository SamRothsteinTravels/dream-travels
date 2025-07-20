"""
Theme Park Service for integrating with thrill-data.com API
Provides crowd predictions, wait times, and attraction management
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

# Configuration - in production these would come from environment variables
THRILL_API_KEY = os.environ.get('THRILL_API_KEY', 'demo-key')  # User needs to provide
THRILL_API_BASE = "https://api.thrill-data.com/v3"  # Hypothetical endpoint

class Attraction(BaseModel):
    id: str
    name: str
    current_wait: int
    historical_average: float
    status: str  # OPERATIONAL, DOWN, DELAYED
    location: Dict[str, float]
    thrill_level: str  # FAMILY, MODERATE, EXTREME
    height_requirement: Optional[str] = None
    fastpass_available: bool = False

class CrowdLevel(BaseModel):
    date: date
    crowd_index: int  # 1-10 scale
    prediction_confidence: float
    peak_times: List[str]
    best_visit_times: List[str]

class ThemePark(BaseModel):
    id: str
    name: str
    location: str
    timezone: str
    attractions: List[Attraction]
    current_crowd_level: int
    today_prediction: CrowdLevel
    tomorrow_prediction: Optional[CrowdLevel]

class WaitTimeEntry(BaseModel):
    timestamp: datetime
    wait_minutes: int
    crowd_level: int

class AttractionHistory(BaseModel):
    attraction_id: str
    date: date
    entries: List[WaitTimeEntry]
    daily_average: float
    peak_wait: int

# Mock data for major theme parks (in production this would come from thrill-data.com)
THEME_PARKS_DATA = {
    "wdw_magic_kingdom": ThemePark(
        id="wdw_magic_kingdom",
        name="Magic Kingdom - Walt Disney World",
        location="Orlando, FL",
        timezone="America/New_York",
        current_crowd_level=6,
        today_prediction=CrowdLevel(
            date=datetime.now().date(),
            crowd_index=6,
            prediction_confidence=0.85,
            peak_times=["11:00 AM - 1:00 PM", "3:00 PM - 6:00 PM"],
            best_visit_times=["8:00 AM - 10:00 AM", "7:00 PM - 9:00 PM"]
        ),
        tomorrow_prediction=CrowdLevel(
            date=datetime.now().date() + timedelta(days=1),
            crowd_index=4,
            prediction_confidence=0.78,
            peak_times=["12:00 PM - 2:00 PM"],
            best_visit_times=["8:00 AM - 11:00 AM", "6:00 PM - 9:00 PM"]
        ),
        attractions=[
            Attraction(
                id="space_mountain",
                name="Space Mountain",
                current_wait=45,
                historical_average=38.2,
                status="OPERATIONAL",
                location={"lat": 28.4189, "lng": -81.5776},
                thrill_level="MODERATE",
                height_requirement="44 inches",
                fastpass_available=True
            ),
            Attraction(
                id="pirates_caribbean",
                name="Pirates of the Caribbean",
                current_wait=25,
                historical_average=22.8,
                status="OPERATIONAL",
                location={"lat": 28.4181, "lng": -81.5839},
                thrill_level="FAMILY",
                fastpass_available=True
            ),
            Attraction(
                id="haunted_mansion",
                name="Haunted Mansion",
                current_wait=35,
                historical_average=31.5,
                status="OPERATIONAL", 
                location={"lat": 28.4201, "lng": -81.5831},
                thrill_level="FAMILY",
                fastpass_available=True
            ),
            Attraction(
                id="big_thunder",
                name="Big Thunder Mountain Railroad",
                current_wait=30,
                historical_average=28.7,
                status="OPERATIONAL",
                location={"lat": 28.4198, "lng": -81.5845},
                thrill_level="MODERATE", 
                height_requirement="40 inches",
                fastpass_available=True
            )
        ]
    ),
    
    "universal_studios_orlando": ThemePark(
        id="universal_studios_orlando",
        name="Universal Studios Florida",
        location="Orlando, FL", 
        timezone="America/New_York",
        current_crowd_level=7,
        today_prediction=CrowdLevel(
            date=datetime.now().date(),
            crowd_index=7,
            prediction_confidence=0.82,
            peak_times=["10:00 AM - 2:00 PM", "4:00 PM - 7:00 PM"],
            best_visit_times=["8:00 AM - 9:30 AM", "8:00 PM - 10:00 PM"]
        ),
        tomorrow_prediction=CrowdLevel(
            date=datetime.now().date() + timedelta(days=1),
            crowd_index=5,
            prediction_confidence=0.75,
            peak_times=["11:00 AM - 1:00 PM"],
            best_visit_times=["8:00 AM - 10:30 AM", "7:00 PM - 10:00 PM"]
        ),
        attractions=[
            Attraction(
                id="harry_potter_escape",
                name="Harry Potter and the Escape from Gringotts",
                current_wait=75,
                historical_average=68.4,
                status="OPERATIONAL",
                location={"lat": 28.4794, "lng": -81.4685},
                thrill_level="MODERATE",
                height_requirement="42 inches",
                fastpass_available=True
            ),
            Attraction(
                id="transformers",
                name="Transformers: The Ride 3D",
                current_wait=40,
                historical_average=35.8,
                status="OPERATIONAL",
                location={"lat": 28.4780, "lng": -81.4692},
                thrill_level="MODERATE",
                height_requirement="40 inches",
                fastpass_available=True
            ),
            Attraction(
                id="mummy",
                name="Revenge of the Mummy",
                current_wait=50,
                historical_average=42.1,
                status="OPERATIONAL",
                location={"lat": 28.4785, "lng": -81.4688},
                thrill_level="EXTREME",
                height_requirement="48 inches",
                fastpass_available=True
            )
        ]
    ),

    "disneyland_california": ThemePark(
        id="disneyland_california",
        name="Disneyland Park",
        location="Anaheim, CA",
        timezone="America/Los_Angeles", 
        current_crowd_level=5,
        today_prediction=CrowdLevel(
            date=datetime.now().date(),
            crowd_index=5,
            prediction_confidence=0.88,
            peak_times=["11:30 AM - 2:30 PM"],
            best_visit_times=["8:00 AM - 11:00 AM", "6:00 PM - 10:00 PM"]
        ),
        tomorrow_prediction=CrowdLevel(
            date=datetime.now().date() + timedelta(days=1),
            crowd_index=6,
            prediction_confidence=0.80,
            peak_times=["10:00 AM - 1:00 PM", "3:00 PM - 5:00 PM"],
            best_visit_times=["8:00 AM - 9:30 AM", "7:30 PM - 10:00 PM"]
        ),
        attractions=[
            Attraction(
                id="rise_resistance",
                name="Star Wars: Rise of the Resistance",
                current_wait=90,
                historical_average=105.2,
                status="OPERATIONAL",
                location={"lat": 33.8121, "lng": -117.9190},
                thrill_level="MODERATE",
                height_requirement="40 inches",
                fastpass_available=False  # Virtual queue only
            ),
            Attraction(
                id="millennium_falcon",
                name="Millennium Falcon: Smugglers Run",
                current_wait=55,
                historical_average=62.8,
                status="OPERATIONAL",
                location={"lat": 33.8125, "lng": -117.9195},
                thrill_level="MODERATE",
                height_requirement="38 inches",
                fastpass_available=True
            ),
            Attraction(
                id="indiana_jones",
                name="Indiana Jones Adventure",
                current_wait=65,
                historical_average=58.9,
                status="OPERATIONAL",
                location={"lat": 33.8115, "lng": -117.9205},
                thrill_level="MODERATE",
                height_requirement="46 inches",
                fastpass_available=True
            )
        ]
    )
}

class ThemeParkService:
    """Service for managing theme park data and predictions"""
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.theme_parks_db
        self.client = httpx.AsyncClient()
        
    async def get_available_parks(self) -> List[ThemePark]:
        """Get list of all available theme parks"""
        return list(THEME_PARKS_DATA.values())
    
    async def get_park_by_id(self, park_id: str) -> Optional[ThemePark]:
        """Get specific theme park by ID"""
        return THEME_PARKS_DATA.get(park_id)
    
    async def get_live_wait_times(self, park_id: str) -> Optional[Dict[str, Any]]:
        """Get current wait times for all attractions in a park"""
        park = THEME_PARKS_DATA.get(park_id)
        if not park:
            return None
            
        # In production, this would call thrill-data.com API
        # For now, we'll simulate live data with some randomization
        import random
        
        live_data = {
            "park_id": park_id,
            "park_name": park.name,
            "last_updated": datetime.now().isoformat(),
            "crowd_level": park.current_crowd_level,
            "attractions": []
        }
        
        for attraction in park.attractions:
            # Simulate some variation in wait times
            variation = random.randint(-10, 15)
            current_wait = max(5, attraction.current_wait + variation)
            
            live_data["attractions"].append({
                "id": attraction.id,
                "name": attraction.name,
                "current_wait": current_wait,
                "status": attraction.status,
                "historical_average": attraction.historical_average,
                "thrill_level": attraction.thrill_level,
                "height_requirement": attraction.height_requirement,
                "fastpass_available": attraction.fastpass_available,
                "wait_difference": current_wait - attraction.historical_average
            })
            
        return live_data
    
    async def get_crowd_predictions(self, park_id: str, target_date: date) -> Optional[Dict[str, Any]]:
        """Get crowd level predictions for a specific date"""
        park = THEME_PARKS_DATA.get(park_id)
        if not park:
            return None
            
        # Use today's prediction if target date is today
        if target_date == datetime.now().date():
            prediction = park.today_prediction
        elif target_date == datetime.now().date() + timedelta(days=1):
            prediction = park.tomorrow_prediction
        else:
            # For future dates, generate a prediction based on historical patterns
            import random
            prediction = CrowdLevel(
                date=target_date,
                crowd_index=random.randint(3, 8),
                prediction_confidence=0.65,
                peak_times=["11:00 AM - 2:00 PM"],
                best_visit_times=["8:00 AM - 10:00 AM", "7:00 PM - 9:00 PM"]
            )
            
        return {
            "park_id": park_id,
            "date": prediction.date.isoformat(),
            "crowd_index": prediction.crowd_index,
            "crowd_description": self._get_crowd_description(prediction.crowd_index),
            "prediction_confidence": prediction.prediction_confidence,
            "peak_times": prediction.peak_times,
            "best_visit_times": prediction.best_visit_times,
            "estimated_wait_multiplier": self._get_wait_multiplier(prediction.crowd_index)
        }
    
    async def get_attraction_history(self, attraction_id: str, days: int = 7) -> Dict[str, Any]:
        """Get historical wait time data for an attraction"""
        # In production, this would query historical data from database
        # For now, simulate historical data
        import random
        
        history = []
        base_wait = 30  # Base wait time
        
        for i in range(days):
            target_date = datetime.now().date() - timedelta(days=i)
            daily_entries = []
            
            # Simulate hourly data points
            for hour in range(8, 22):  # 8 AM to 10 PM
                wait_time = base_wait + random.randint(-15, 25)
                if hour in [11, 12, 13, 16, 17, 18]:  # Peak hours
                    wait_time += random.randint(10, 30)
                    
                daily_entries.append({
                    "time": f"{hour:02d}:00",
                    "wait_minutes": max(5, wait_time),
                    "crowd_level": random.randint(3, 8)
                })
                
            history.append({
                "date": target_date.isoformat(),
                "entries": daily_entries,
                "daily_average": sum(entry["wait_minutes"] for entry in daily_entries) / len(daily_entries)
            })
            
        return {
            "attraction_id": attraction_id,
            "history": history
        }
    
    async def optimize_park_plan(self, park_id: str, selected_attractions: List[str], 
                                visit_date: date, arrival_time: str = "08:00") -> Dict[str, Any]:
        """Generate optimized touring plan for selected attractions"""
        park = THEME_PARKS_DATA.get(park_id)
        if not park:
            return None
            
        crowd_prediction = await self.get_crowd_predictions(park_id, visit_date)
        
        # Filter attractions based on selection
        selected_attraction_objects = [
            attr for attr in park.attractions 
            if attr.id in selected_attractions
        ]
        
        # Simple optimization: visit high-wait attractions during low-crowd times
        optimized_plan = []
        current_time = datetime.strptime(arrival_time, "%H:%M").time()
        
        # Sort by expected wait time (highest first for morning)
        sorted_attractions = sorted(
            selected_attraction_objects,
            key=lambda x: x.historical_average * crowd_prediction["estimated_wait_multiplier"],
            reverse=True
        )
        
        for i, attraction in enumerate(sorted_attractions):
            estimated_wait = int(
                attraction.historical_average * crowd_prediction["estimated_wait_multiplier"]
            )
            
            # Add time increment
            time_increment = timedelta(minutes=30 + estimated_wait + 10)  # Wait + ride + walk time
            visit_time = (datetime.combine(visit_date, current_time) + 
                         timedelta(minutes=i * 45)).time()
            
            optimized_plan.append({
                "order": i + 1,
                "attraction": {
                    "id": attraction.id,
                    "name": attraction.name,
                    "thrill_level": attraction.thrill_level
                },
                "recommended_time": visit_time.strftime("%I:%M %p"),
                "estimated_wait": estimated_wait,
                "tips": self._get_attraction_tips(attraction, crowd_prediction["crowd_index"])
            })
            
        return {
            "park_id": park_id,
            "visit_date": visit_date.isoformat(),
            "crowd_level": crowd_prediction["crowd_index"],
            "total_attractions": len(optimized_plan),
            "estimated_total_time": f"{len(optimized_plan) * 45} minutes",
            "plan": optimized_plan,
            "general_tips": [
                f"Best times to visit: {', '.join(crowd_prediction['best_visit_times'])}",
                f"Avoid peak times: {', '.join(crowd_prediction['peak_times'])}",
                "Use mobile order for dining to save time",
                "Download the park's official app for real-time updates"
            ]
        }
    
    def _get_crowd_description(self, crowd_index: int) -> str:
        """Convert crowd index to human-readable description"""
        descriptions = {
            1: "Ghost Town", 2: "Very Light", 3: "Light", 4: "Moderate",
            5: "Busy", 6: "Very Busy", 7: "Packed", 8: "Extremely Packed",
            9: "Avoid at All Costs", 10: "Closed Due to Capacity"
        }
        return descriptions.get(crowd_index, "Unknown")
    
    def _get_wait_multiplier(self, crowd_index: int) -> float:
        """Get wait time multiplier based on crowd level"""
        multipliers = {
            1: 0.3, 2: 0.5, 3: 0.7, 4: 0.9, 5: 1.0,
            6: 1.3, 7: 1.6, 8: 2.0, 9: 2.5, 10: 3.0
        }
        return multipliers.get(crowd_index, 1.0)
    
    def _get_attraction_tips(self, attraction: Attraction, crowd_level: int) -> List[str]:
        """Get specific tips for an attraction based on crowd level"""
        tips = []
        
        if attraction.fastpass_available:
            tips.append("FastPass/Lightning Lane available - highly recommended!")
            
        if crowd_level >= 7:
            tips.append("Consider visiting during parade times for shorter waits")
            
        if attraction.thrill_level == "EXTREME":
            tips.append("Check height requirements before queuing")
            
        if attraction.height_requirement:
            tips.append(f"Height requirement: {attraction.height_requirement}")
            
        return tips
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()