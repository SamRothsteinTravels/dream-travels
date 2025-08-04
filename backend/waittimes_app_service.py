"""
WaitTimesApp API Service
Integrates with WaitTimesApp (Wartezeiten.APP) for additional theme park data
Complements queue-times.com with international park coverage
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import json

logger = logging.getLogger(__name__)

# WaitTimesApp API Configuration - user needs to provide API key
WAITTIMES_APP_API_KEY = os.environ.get('WAITTIMES_APP_API_KEY', None)
WAITTIMES_APP_BASE_URL = "https://api.wartezeiten.app"  # Estimated URL

class WaitTimesAppAttraction(BaseModel):
    id: str
    name: str
    wait_time: Optional[int] = None
    status: str = "unknown"
    location: Optional[Dict[str, Any]] = None
    attraction_type: str = "ride"

class WaitTimesAppPark(BaseModel):
    id: str
    name: str
    country: str
    timezone: str
    attractions: List[WaitTimesAppAttraction] = []

class WaitTimesAppService:
    """Service for integrating with WaitTimesApp API"""
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.waittimes_app_db
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'TravelMate-Pro/1.0',
                'Accept': 'application/json'
            }
        )
        self.base_url = WAITTIMES_APP_BASE_URL
        self.api_key = WAITTIMES_APP_API_KEY
        
        # Mock data structure for demonstration (when API key not available)
        self.mock_parks = {
            "europa_park": {
                "id": "europa_park",
                "name": "Europa-Park",
                "country": "Germany",
                "timezone": "Europe/Berlin",
                "attractions": [
                    {
                        "id": "blue_fire",
                        "name": "Blue Fire Megacoaster",
                        "wait_time": 35,
                        "status": "operating",
                        "attraction_type": "roller_coaster"
                    },
                    {
                        "id": "silver_star",
                        "name": "Silver Star",
                        "wait_time": 45,
                        "status": "operating", 
                        "attraction_type": "roller_coaster"
                    }
                ]
            },
            "phantasialand": {
                "id": "phantasialand",
                "name": "Phantasialand",
                "country": "Germany",
                "timezone": "Europe/Berlin",
                "attractions": [
                    {
                        "id": "taron",
                        "name": "Taron",
                        "wait_time": 55,
                        "status": "operating",
                        "attraction_type": "roller_coaster"
                    },
                    {
                        "id": "black_mamba",
                        "name": "Black Mamba",
                        "wait_time": 25,
                        "status": "operating",
                        "attraction_type": "roller_coaster"
                    }
                ]
            },
            "efteling": {
                "id": "efteling",
                "name": "Efteling",
                "country": "Netherlands",
                "timezone": "Europe/Amsterdam",
                "attractions": [
                    {
                        "id": "baron_1898",
                        "name": "Baron 1898",
                        "wait_time": 30,
                        "status": "operating",
                        "attraction_type": "roller_coaster"
                    },
                    {
                        "id": "flying_dutchman",
                        "name": "De Vliegende Hollander",
                        "wait_time": 20,
                        "status": "operating",
                        "attraction_type": "water_ride"
                    }
                ]
            }
        }
    
    async def get_available_parks(self) -> List[Dict[str, Any]]:
        """Get list of available parks from WaitTimesApp"""
        try:
            logger.info("Fetching available parks from WaitTimesApp")
            
            # Check cache first
            cache_key = "waittimes_app_parks_list"
            cached_parks = await self._get_cached_data(cache_key)
            if cached_parks:
                return cached_parks
            
            if not self.api_key:
                logger.warning("No WaitTimesApp API key provided, using mock data")
                return await self._get_mock_parks()
            
            # Make API request
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await self.client.get(f"{self.base_url}/parks", headers=headers)
                response.raise_for_status()
                
                parks_data = response.json()
                processed_parks = []
                
                # Process API response
                for park in parks_data.get("parks", []):
                    processed_park = {
                        "id": str(park.get("id", "")),
                        "name": park.get("name", "Unknown Park"),
                        "country": park.get("country", ""),
                        "timezone": park.get("timezone", "UTC"),
                        "coordinates": {
                            "latitude": park.get("latitude"),
                            "longitude": park.get("longitude")
                        },
                        "source": "waittimes-app"
                    }
                    processed_parks.append(processed_park)
                
                # Cache for 4 hours
                await self._cache_data(cache_key, processed_parks, ttl_hours=4)
                
                logger.info(f"Retrieved {len(processed_parks)} parks from WaitTimesApp")
                return processed_parks
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    logger.error("Invalid WaitTimesApp API key")
                else:
                    logger.error(f"WaitTimesApp API error: {e.response.status_code}")
                return await self._get_mock_parks()
                
        except Exception as e:
            logger.error(f"Error fetching parks from WaitTimesApp: {e}")
            return await self._get_mock_parks()
    
    async def _get_mock_parks(self) -> List[Dict[str, Any]]:
        """Return mock park data when API is not available"""
        mock_parks = []
        for park_id, park_data in self.mock_parks.items():
            mock_parks.append({
                "id": park_id,
                "name": park_data["name"],
                "country": park_data["country"],
                "timezone": park_data["timezone"],
                "coordinates": {"latitude": None, "longitude": None},
                "source": "waittimes-app-mock"
            })
        return mock_parks
    
    async def get_park_by_id(self, park_id: str) -> Optional[Dict[str, Any]]:
        """Get specific park information by ID"""
        try:
            all_parks = await self.get_available_parks()
            for park in all_parks:
                if park["id"] == park_id:
                    return park
            return None
        except Exception as e:
            logger.error(f"Error getting park {park_id}: {e}")
            return None
    
    async def get_live_wait_times(self, park_id: str) -> Optional[Dict[str, Any]]:
        """Get current wait times for all attractions in a park"""
        try:
            logger.info(f"Fetching wait times for park {park_id} from WaitTimesApp")
            
            # Check cache first (5 minute cache for real-time data)
            cache_key = f"waittimes_app_wait_{park_id}"
            cached_data = await self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            if not self.api_key:
                return await self._get_mock_wait_times(park_id)
            
            # Make API request
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await self.client.get(
                    f"{self.base_url}/parks/{park_id}/wait-times", 
                    headers=headers
                )
                response.raise_for_status()
                
                wait_data = response.json()
                processed_data = self._process_wait_times_response(wait_data, park_id)
                
                # Cache for 5 minutes
                await self._cache_data(cache_key, processed_data, ttl_minutes=5)
                
                return processed_data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"WaitTimesApp API error for park {park_id}: {e.response.status_code}")
                return await self._get_mock_wait_times(park_id)
                
        except Exception as e:
            logger.error(f"Error fetching wait times for park {park_id}: {e}")
            return await self._get_mock_wait_times(park_id)
    
    async def _get_mock_wait_times(self, park_id: str) -> Optional[Dict[str, Any]]:
        """Return mock wait times data"""
        if park_id not in self.mock_parks:
            return None
        
        park_data = self.mock_parks[park_id]
        
        # Add some randomization to make it more realistic
        import random
        attractions = []
        total_wait = 0
        open_count = 0
        max_wait = 0
        
        for attraction in park_data["attractions"]:
            # Add some random variation
            base_wait = attraction["wait_time"]
            variation = random.randint(-10, 15)
            wait_time = max(5, base_wait + variation)
            
            processed_attraction = {
                "id": attraction["id"],
                "name": attraction["name"],
                "wait_time": wait_time,
                "is_open": True,
                "status": "OPERATIONAL",
                "last_updated": datetime.utcnow().isoformat(),
                "attraction_type": attraction.get("attraction_type", "ride"),
                "land": "Main Area",  # Mock land
                "land_id": "main",
                "thrill_level": "MODERATE",
                "height_requirement": None,
                "fastpass_available": True
            }
            
            attractions.append(processed_attraction)
            total_wait += wait_time
            open_count += 1
            max_wait = max(max_wait, wait_time)
        
        return {
            "park_id": park_id,
            "park_name": park_data["name"],
            "last_updated": datetime.utcnow().isoformat(),
            "attractions": attractions,
            "summary": {
                "total_attractions": len(attractions),
                "open_attractions": open_count,
                "average_wait": round(total_wait / open_count, 1) if open_count > 0 else 0,
                "max_wait": max_wait
            },
            "source": "waittimes-app-mock"
        }
    
    def _process_wait_times_response(self, wait_data: Dict[str, Any], park_id: str) -> Dict[str, Any]:
        """Process the API response for wait times"""
        processed_data = {
            "park_id": park_id,
            "last_updated": datetime.utcnow().isoformat(),
            "attractions": [],
            "summary": {
                "total_attractions": 0,
                "open_attractions": 0,
                "average_wait": 0,
                "max_wait": 0
            },
            "source": "waittimes-app"
        }
        
        total_wait = 0
        wait_count = 0
        max_wait = 0
        
        # Process attractions from API response
        attractions = wait_data.get("attractions", [])
        for attraction in attractions:
            wait_time = attraction.get("wait_time", 0)
            is_open = attraction.get("is_open", True)
            
            processed_attraction = {
                "id": str(attraction.get("id", "")),
                "name": attraction.get("name", "Unknown Attraction"),
                "wait_time": wait_time if wait_time is not None else 0,
                "is_open": is_open,
                "status": "OPERATIONAL" if is_open else "CLOSED",
                "last_updated": attraction.get("last_updated", processed_data["last_updated"]),
                "attraction_type": attraction.get("type", "ride"),
                "land": attraction.get("area", "Main Area"),
                "land_id": attraction.get("area_id", "main"),
                "thrill_level": attraction.get("thrill_level", "UNKNOWN"),
                "height_requirement": attraction.get("height_requirement"),
                "fastpass_available": attraction.get("fast_pass", False)
            }
            
            processed_data["attractions"].append(processed_attraction)
            processed_data["summary"]["total_attractions"] += 1
            
            if is_open:
                processed_data["summary"]["open_attractions"] += 1
                if wait_time and wait_time > 0:
                    total_wait += wait_time
                    wait_count += 1
                    max_wait = max(max_wait, wait_time)
        
        # Calculate summary statistics
        if wait_count > 0:
            processed_data["summary"]["average_wait"] = round(total_wait / wait_count, 1)
        processed_data["summary"]["max_wait"] = max_wait
        
        return processed_data
    
    async def get_crowd_predictions(self, park_id: str, target_date: date) -> Optional[Dict[str, Any]]:
        """Get crowd level predictions from WaitTimesApp"""
        try:
            if not self.api_key:
                return await self._get_mock_crowd_predictions(park_id, target_date)
            
            # Check cache first
            cache_key = f"waittimes_app_crowd_{park_id}_{target_date}"
            cached_data = await self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            # Make API request
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = await self.client.get(
                    f"{self.base_url}/parks/{park_id}/crowd-calendar",
                    headers=headers,
                    params={"date": target_date.isoformat()}
                )
                response.raise_for_status()
                
                crowd_data = response.json()
                processed_data = self._process_crowd_response(crowd_data, park_id, target_date)
                
                # Cache for 30 minutes
                await self._cache_data(cache_key, processed_data, ttl_minutes=30)
                
                return processed_data
                
            except httpx.HTTPStatusError as e:
                logger.error(f"WaitTimesApp crowd API error: {e.response.status_code}")
                return await self._get_mock_crowd_predictions(park_id, target_date)
                
        except Exception as e:
            logger.error(f"Error fetching crowd predictions: {e}")
            return await self._get_mock_crowd_predictions(park_id, target_date)
    
    async def _get_mock_crowd_predictions(self, park_id: str, target_date: date) -> Optional[Dict[str, Any]]:
        """Generate mock crowd predictions"""
        import random
        
        # Generate crowd level based on day of week
        weekday = target_date.weekday()
        if weekday in [5, 6]:  # Weekend
            base_crowd = random.randint(6, 8)
        else:  # Weekday
            base_crowd = random.randint(3, 6)
        
        crowd_descriptions = {
            1: "Ghost Town", 2: "Very Light", 3: "Light", 4: "Moderate",
            5: "Busy", 6: "Very Busy", 7: "Packed", 8: "Extremely Packed"
        }
        
        return {
            "park_id": park_id,
            "date": target_date.isoformat(),
            "crowd_index": base_crowd,
            "crowd_description": crowd_descriptions.get(base_crowd, "Unknown"),
            "prediction_confidence": 0.75,
            "peak_times": ["11:00 AM - 2:00 PM", "4:00 PM - 6:00 PM"],
            "best_visit_times": ["8:00 AM - 10:00 AM", "7:00 PM - 9:00 PM"],
            "estimated_wait_multiplier": 1.0 + (base_crowd - 5) * 0.2,
            "source": "waittimes-app-mock"
        }
    
    def _process_crowd_response(self, crowd_data: Dict[str, Any], park_id: str, target_date: date) -> Dict[str, Any]:
        """Process crowd prediction API response"""
        crowd_level = crowd_data.get("crowd_level", 5)
        
        crowd_descriptions = {
            1: "Ghost Town", 2: "Very Light", 3: "Light", 4: "Moderate",
            5: "Busy", 6: "Very Busy", 7: "Packed", 8: "Extremely Packed",
            9: "Avoid at All Costs", 10: "Closed Due to Capacity"
        }
        
        return {
            "park_id": park_id,
            "date": target_date.isoformat(),
            "crowd_index": crowd_level,
            "crowd_description": crowd_descriptions.get(crowd_level, "Unknown"),
            "prediction_confidence": crowd_data.get("confidence", 0.8),
            "peak_times": crowd_data.get("peak_times", []),
            "best_visit_times": crowd_data.get("best_times", []),
            "estimated_wait_multiplier": crowd_data.get("wait_multiplier", 1.0),
            "weather_impact": crowd_data.get("weather_impact"),
            "special_events": crowd_data.get("events", []),
            "source": "waittimes-app"
        }
    
    async def optimize_park_plan(self, park_id: str, selected_attractions: List[str], 
                                visit_date: date, arrival_time: str = "09:00") -> Dict[str, Any]:
        """Generate optimized touring plan using WaitTimesApp data"""
        try:
            wait_data = await self.get_live_wait_times(park_id)
            crowd_data = await self.get_crowd_predictions(park_id, visit_date)
            
            if not wait_data:
                return {"error": "Unable to fetch wait times data"}
            
            # Filter selected attractions
            all_attractions = wait_data["attractions"]
            selected_attraction_objects = [
                attr for attr in all_attractions 
                if attr["id"] in selected_attractions and attr["is_open"]
            ]
            
            if not selected_attraction_objects:
                return {"error": "No valid attractions selected"}
            
            # Sort by wait time for efficient routing
            sorted_attractions = sorted(
                selected_attraction_objects,
                key=lambda x: x["wait_time"] if x["wait_time"] else 0
            )
            
            # Generate optimized plan
            optimized_plan = []
            current_time = datetime.strptime(arrival_time, "%H:%M").time()
            
            for i, attraction in enumerate(sorted_attractions):
                time_increment = timedelta(minutes=i * 40)  # 40 minutes per attraction
                visit_time = (datetime.combine(visit_date, current_time) + time_increment).time()
                
                tips = []
                if attraction["wait_time"] > 45:
                    tips.append("High wait time - consider visiting during off-peak hours")
                if attraction["fastpass_available"]:
                    tips.append("FastPass/Express Pass available")
                if attraction["height_requirement"]:
                    tips.append(f"Height requirement: {attraction['height_requirement']}")
                
                optimized_plan.append({
                    "order": i + 1,
                    "attraction": {
                        "id": attraction["id"],
                        "name": attraction["name"],
                        "land": attraction["land"]
                    },
                    "recommended_time": visit_time.strftime("%I:%M %p"),
                    "estimated_wait": attraction["wait_time"],
                    "tips": tips
                })
            
            crowd_info = crowd_data or {"crowd_index": 5, "crowd_description": "Moderate"}
            
            return {
                "park_id": park_id,
                "visit_date": visit_date.isoformat(),
                "crowd_level": crowd_info["crowd_index"],
                "crowd_description": crowd_info["crowd_description"],
                "total_attractions": len(optimized_plan),
                "estimated_total_time": f"{len(optimized_plan) * 40} minutes",
                "plan": optimized_plan,
                "general_tips": [
                    f"Crowd level: {crowd_info['crowd_description']}",
                    "Arrive early for shorter wait times",
                    "Consider mobile food ordering to save time",
                    "Data powered by WaitTimesApp"
                ],
                "data_source": "waittimes-app"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing park plan: {e}")
            return {"error": f"Failed to optimize park plan: {str(e)}"}
    
    async def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached data from database"""
        try:
            collection = self.db.cache
            cached_doc = await collection.find_one({"cache_key": cache_key})
            
            if cached_doc:
                cache_time = cached_doc.get("cached_at")
                ttl_minutes = cached_doc.get("ttl_minutes", 60)
                
                if cache_time:
                    cache_datetime = datetime.fromisoformat(cache_time)
                    if (datetime.utcnow() - cache_datetime).total_seconds() < (ttl_minutes * 60):
                        return cached_doc.get("data")
            
            return None
        except Exception as e:
            logger.error(f"Error getting cached data: {e}")
            return None
    
    async def _cache_data(self, cache_key: str, data: Dict[str, Any], ttl_minutes: int = 60, ttl_hours: int = 0) -> None:
        """Cache data in database"""
        try:
            collection = self.db.cache
            ttl_total_minutes = ttl_minutes + (ttl_hours * 60)
            
            cache_doc = {
                "cache_key": cache_key,
                "data": data,
                "cached_at": datetime.utcnow().isoformat(),
                "ttl_minutes": ttl_total_minutes
            }
            
            await collection.replace_one(
                {"cache_key": cache_key},
                cache_doc,
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error caching data: {e}")
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()