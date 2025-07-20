"""
FastAPI routes for theme park functionality
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field
from theme_park_service import ThemeParkService, ThemePark
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Get MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)

# Initialize theme park service
theme_park_service = ThemeParkService(client)

# Router
theme_park_router = APIRouter(prefix="/api/theme-parks", tags=["theme-parks"])

# Pydantic models for requests
class ParkPlanRequest(BaseModel):
    park_id: str
    selected_attractions: List[str]
    visit_date: str  # ISO format date
    arrival_time: str = "08:00"  # HH:MM format

class AttractionSelection(BaseModel):
    attraction_id: str
    priority: int = Field(ge=1, le=5, description="Priority level 1-5")
    preferred_time: Optional[str] = None  # HH:MM format

@theme_park_router.get("/parks")
async def get_available_parks():
    """Get list of all available theme parks"""
    parks = await theme_park_service.get_available_parks()
    
    # Convert to simplified format for frontend
    parks_data = []
    for park in parks:
        parks_data.append({
            "id": park.id,
            "name": park.name,
            "location": park.location,
            "current_crowd_level": park.current_crowd_level,
            "crowd_description": theme_park_service._get_crowd_description(park.current_crowd_level),
            "total_attractions": len(park.attractions),
            "timezone": park.timezone
        })
    
    return {"parks": parks_data}

@theme_park_router.get("/parks/{park_id}")
async def get_park_details(park_id: str):
    """Get detailed information about a specific theme park"""
    park = await theme_park_service.get_park_by_id(park_id)
    
    if not park:
        raise HTTPException(status_code=404, detail="Theme park not found")
    
    return {
        "park": park.dict(),
        "crowd_prediction_today": park.today_prediction.dict(),
        "crowd_prediction_tomorrow": park.tomorrow_prediction.dict() if park.tomorrow_prediction else None
    }

@theme_park_router.get("/parks/{park_id}/wait-times")
async def get_live_wait_times(park_id: str):
    """Get current wait times for all attractions in a park"""
    wait_times = await theme_park_service.get_live_wait_times(park_id)
    
    if not wait_times:
        raise HTTPException(status_code=404, detail="Theme park not found")
    
    return wait_times

@theme_park_router.get("/parks/{park_id}/crowds/{target_date}")
async def get_crowd_predictions(park_id: str, target_date: str):
    """Get crowd level predictions for a specific date"""
    try:
        parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    predictions = await theme_park_service.get_crowd_predictions(park_id, parsed_date)
    
    if not predictions:
        raise HTTPException(status_code=404, detail="Theme park not found")
    
    return predictions

@theme_park_router.get("/attractions/{attraction_id}/history")
async def get_attraction_history(
    attraction_id: str,
    days: int = Query(7, ge=1, le=30, description="Number of days of history to retrieve")
):
    """Get historical wait time data for an attraction"""
    history = await theme_park_service.get_attraction_history(attraction_id, days)
    return history

@theme_park_router.post("/parks/{park_id}/optimize-plan")
async def optimize_park_plan(park_id: str, request: ParkPlanRequest):
    """Generate optimized touring plan for selected attractions"""
    try:
        visit_date = datetime.strptime(request.visit_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if not request.selected_attractions:
        raise HTTPException(status_code=400, detail="At least one attraction must be selected")
    
    optimized_plan = await theme_park_service.optimize_park_plan(
        park_id=park_id,
        selected_attractions=request.selected_attractions,
        visit_date=visit_date,
        arrival_time=request.arrival_time
    )
    
    if not optimized_plan:
        raise HTTPException(status_code=404, detail="Theme park not found")
    
    return optimized_plan

@theme_park_router.get("/parks/{park_id}/attractions")
async def get_park_attractions(
    park_id: str,
    thrill_level: Optional[str] = Query(None, description="Filter by thrill level: FAMILY, MODERATE, EXTREME"),
    fastpass_only: bool = Query(False, description="Show only FastPass/Lightning Lane attractions")
):
    """Get detailed list of attractions for a specific park with filtering options"""
    park = await theme_park_service.get_park_by_id(park_id)
    
    if not park:
        raise HTTPException(status_code=404, detail="Theme park not found")
    
    attractions = park.attractions
    
    # Apply filters
    if thrill_level:
        attractions = [attr for attr in attractions if attr.thrill_level == thrill_level.upper()]
    
    if fastpass_only:
        attractions = [attr for attr in attractions if attr.fastpass_available]
    
    # Get current wait times
    wait_times_data = await theme_park_service.get_live_wait_times(park_id)
    wait_times_map = {
        attr["id"]: attr["current_wait"] 
        for attr in wait_times_data.get("attractions", [])
    }
    
    # Format response
    attractions_data = []
    for attraction in attractions:
        current_wait = wait_times_map.get(attraction.id, attraction.current_wait)
        
        attractions_data.append({
            "id": attraction.id,
            "name": attraction.name,
            "current_wait": current_wait,
            "historical_average": attraction.historical_average,
            "status": attraction.status,
            "thrill_level": attraction.thrill_level,
            "height_requirement": attraction.height_requirement,
            "fastpass_available": attraction.fastpass_available,
            "wait_difference": current_wait - attraction.historical_average,
            "location": attraction.location
        })
    
    return {
        "park_id": park_id,
        "park_name": park.name,
        "attractions": attractions_data,
        "total_count": len(attractions_data),
        "filters_applied": {
            "thrill_level": thrill_level,
            "fastpass_only": fastpass_only
        }
    }

@theme_park_router.get("/compare-parks")
async def compare_parks(
    park_ids: str = Query(..., description="Comma-separated list of park IDs to compare"),
    comparison_date: Optional[str] = Query(None, description="Date for comparison (YYYY-MM-DD)")
):
    """Compare crowd levels and wait times across multiple parks"""
    park_id_list = [pid.strip() for pid in park_ids.split(",")]
    
    if len(park_id_list) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 parks can be compared at once")
    
    comparison_data = []
    target_date = datetime.now().date()
    
    if comparison_date:
        try:
            target_date = datetime.strptime(comparison_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    for park_id in park_id_list:
        park = await theme_park_service.get_park_by_id(park_id)
        if not park:
            continue
            
        wait_times = await theme_park_service.get_live_wait_times(park_id)
        crowd_prediction = await theme_park_service.get_crowd_predictions(park_id, target_date)
        
        # Calculate average wait time
        avg_wait = sum(attr["current_wait"] for attr in wait_times["attractions"]) / len(wait_times["attractions"])
        
        comparison_data.append({
            "park_id": park_id,
            "park_name": park.name,
            "location": park.location,
            "crowd_level": crowd_prediction["crowd_index"],
            "crowd_description": crowd_prediction["crowd_description"],
            "average_wait_time": round(avg_wait, 1),
            "total_attractions": len(park.attractions),
            "best_visit_times": crowd_prediction["best_visit_times"],
            "prediction_confidence": crowd_prediction["prediction_confidence"]
        })
    
    # Sort by crowd level (lowest first)
    comparison_data.sort(key=lambda x: x["crowd_level"])
    
    return {
        "comparison_date": target_date.isoformat(),
        "parks": comparison_data,
        "recommendation": {
            "best_park": comparison_data[0] if comparison_data else None,
            "least_crowded": min(comparison_data, key=lambda x: x["crowd_level"]) if comparison_data else None,
            "shortest_waits": min(comparison_data, key=lambda x: x["average_wait_time"]) if comparison_data else None
        }
    }

# Health check endpoint
@theme_park_router.get("/health")
async def theme_park_health_check():
    """Health check for theme park service"""
    return {
        "status": "healthy",
        "service": "theme_park_service",
        "timestamp": datetime.now().isoformat(),
        "available_parks": len(await theme_park_service.get_available_parks())
    }