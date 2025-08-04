"""
WaitTimesApp API Service
Integrates with WaitTimesApp (Wartezeiten.APP) for theme park data
Real API integration - NO API KEY REQUIRED (Public API)
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

# WaitTimesApp API Configuration - NO API KEY NEEDED!
WAITTIMES_APP_BASE_URL = "https://api.wartezeiten.app"

class WaitTimesAppAttraction(BaseModel):
    uuid: str
    code: str
    name: str
    waitingtime: int
    status: str
    datetime: str
    date: str
    time: str

class WaitTimesAppPark(BaseModel):
    id: str
    uuid: str
    name: str
    land: str

class WaitTimesAppService:
    """Service for integrating with WaitTimesApp API (Wartezeiten.APP)"""
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.waittimes_app_db
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Dream-Travels/1.0',
                'Accept': 'application/json'
            }
        )
        self.base_url = WAITTIMES_APP_BASE_URL
        
        # Rate limiting: Max 10 requests per 60 seconds per endpoint
        self.rate_limit_window = 60
        self.max_requests = 10
        
    async def get_available_parks(self) -> List[Dict[str, Any]]:
        """Get list of available parks from WaitTimesApp API (Real API - No Key Required)"""
        try:
            logger.info("Fetching available parks from WaitTimesApp (Real API)")
            
            # Check cache first
            cache_key = "waittimes_app_parks_list_real"
            cached_parks = await self._get_cached_data(cache_key)
            if cached_parks:
                return cached_parks
            
            # Make API request with required language header
            headers = {
                'language': 'en',  # Use English language
                'Accept': 'application/json'
            }
            
            response = await self.client.get(f"{self.base_url}/v1/parks", headers=headers)
            response.raise_for_status()
            
            parks_data = response.json()
            processed_parks = []
            
            # Process the API response
            for park in parks_data:
                processed_park = {
                    "id": park.get("id", ""),
                    "uuid": park.get("uuid", ""),
                    "name": park.get("name", "Unknown Park"),
                    "country": park.get("land", ""),  # 'land' means country in the API
                    "timezone": self._get_timezone_for_country(park.get("land", "")),
                    "coordinates": {"latitude": None, "longitude": None},  # Not provided by API
                    "source": "waittimes-app-real"
                }
                processed_parks.append(processed_park)
            
            # Cache for 24 hours (API caches for 24 hours)
            await self._cache_data(cache_key, processed_parks, ttl_hours=24)
            
            logger.info(f"Successfully retrieved {len(processed_parks)} parks from WaitTimesApp API")
            return processed_parks
            
        except httpx.HTTPStatusError as e:
            logger.error(f"WaitTimesApp API HTTP error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                logger.warning("Rate limit exceeded for WaitTimesApp API - using fallback")
            return await self._get_fallback_parks()
            
        except Exception as e:
            logger.error(f"Error fetching parks from WaitTimesApp: {e}")
            return await self._get_fallback_parks()
    
    async def get_park_by_id(self, park_id: str) -> Optional[Dict[str, Any]]:
        """Get specific park information by ID"""
        try:
            all_parks = await self.get_available_parks()
            for park in all_parks:
                if park["id"] == park_id or park["uuid"] == park_id:
                    return park
            return None
        except Exception as e:
            logger.error(f"Error getting park {park_id}: {e}")
            return None
    
    async def get_live_wait_times(self, park_id: str) -> Optional[Dict[str, Any]]:
        """Get current wait times for all attractions in a park (Real API)"""
        try:
            logger.info(f"Fetching wait times for park {park_id} from WaitTimesApp (Real API)")
            
            # Check cache first (5 minute cache matching API cache)
            cache_key = f"waittimes_app_wait_real_{park_id}"
            cached_data = await self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            # Get park info to determine the correct park identifier
            park_info = await self.get_park_by_id(park_id)
            if not park_info:
                logger.error(f"Park {park_id} not found")
                return None
            
            # Use UUID if available, otherwise use ID
            park_identifier = park_info.get("uuid", park_info.get("id", park_id))
            
            # Make API request with required headers
            headers = {
                'park': park_identifier,
                'language': 'en',
                'Accept': 'application/json'
            }
            
            response = await self.client.get(f"{self.base_url}/v1/waitingtimes", headers=headers)
            response.raise_for_status()
            
            wait_data = response.json()
            processed_data = self._process_real_wait_times_response(wait_data, park_id, park_info["name"])
            
            # Cache for 5 minutes (matching API cache)
            await self._cache_data(cache_key, processed_data, ttl_minutes=5)
            
            return processed_data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"WaitTimesApp API error for park {park_id}: {e.response.status_code}")
            if e.response.status_code == 404:
                return {"error": f"No wait time data available for park {park_id}"}
            elif e.response.status_code == 429:
                logger.warning("Rate limit exceeded - wait times unavailable")
                return {"error": "Rate limit exceeded, please try again later"}
            return None
            
        except Exception as e:
            logger.error(f"Error fetching wait times for park {park_id}: {e}")
            return None
    
    def _process_real_wait_times_response(self, wait_data: List[Dict[str, Any]], park_id: str, park_name: str) -> Dict[str, Any]:
        """Process the real API response for wait times"""
        processed_data = {
            "park_id": park_id,
            "park_name": park_name,
            "last_updated": datetime.utcnow().isoformat(),
            "attractions": [],
            "summary": {
                "total_attractions": 0,
                "open_attractions": 0,
                "average_wait": 0,
                "max_wait": 0
            },
            "source": "waittimes-app-real"
        }
        
        total_wait = 0
        wait_count = 0
        max_wait = 0
        
        # Process attractions from API response
        for attraction in wait_data:
            wait_time = attraction.get("waitingtime", 0)
            status = attraction.get("status", "closed")
            is_open = status == "opened"
            
            processed_attraction = {
                "id": attraction.get("uuid", attraction.get("code", "")),
                "code": attraction.get("code", ""),
                "name": attraction.get("name", "Unknown Attraction"),
                "wait_time": wait_time if wait_time is not None else 0,
                "is_open": is_open,
                "status": self._normalize_status(status),
                "last_updated": attraction.get("datetime", processed_data["last_updated"]),
                "attraction_type": "ride",  # API doesn't specify type
                "land": "Main Area",  # API doesn't provide land information
                "land_id": "main",
                "thrill_level": "UNKNOWN",
                "height_requirement": None,
                "fastpass_available": status == "virtualqueue"  # Virtual queue indicates fastpass-like system
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
    
    def _normalize_status(self, status: str) -> str:
        """Normalize attraction status to common format"""
        status_mapping = {
            "opened": "OPERATIONAL",
            "virtualqueue": "VIRTUAL_QUEUE",
            "maintenance": "DOWN",
            "closedice": "CLOSED",
            "closedweather": "CLOSED",
            "closed": "CLOSED"
        }
        return status_mapping.get(status.lower(), "UNKNOWN")
    
    async def get_park_opening_hours(self, park_id: str) -> Optional[Dict[str, Any]]:
        """Get opening hours for a specific park"""
        try:
            park_info = await self.get_park_by_id(park_id)
            if not park_info:
                return None
            
            park_identifier = park_info.get("uuid", park_info.get("id", park_id))
            
            headers = {
                'park': park_identifier,
                'Accept': 'application/json'
            }
            
            response = await self.client.get(f"{self.base_url}/v1/openingtimes", headers=headers)
            response.raise_for_status()
            
            opening_data = response.json()
            
            if opening_data and len(opening_data) > 0:
                hours = opening_data[0]  # Take first entry
                return {
                    "park_id": park_id,
                    "is_open_today": hours.get("opened_today", False),
                    "opening_time": hours.get("open_from"),
                    "closing_time": hours.get("closed_from"),
                    "source": "waittimes-app-real"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching opening hours for park {park_id}: {e}")
            return None
    
    async def get_crowd_predictions(self, park_id: str, target_date: date) -> Optional[Dict[str, Any]]:
        """Generate crowd predictions based on current wait times (API doesn't provide crowd data)"""
        try:
            wait_data = await self.get_live_wait_times(park_id)
            if not wait_data or wait_data.get("error"):
                return None
            
            # Calculate crowd level based on average wait times
            avg_wait = wait_data["summary"]["average_wait"]
            max_wait = wait_data["summary"]["max_wait"]
            
            # Determine crowd level (1-10 scale) based on wait times
            if avg_wait <= 5:
                crowd_index = 1
                crowd_description = "Very Light"
            elif avg_wait <= 15:
                crowd_index = 2
                crowd_description = "Light"
            elif avg_wait <= 25:
                crowd_index = 3
                crowd_description = "Moderate"
            elif avg_wait <= 35:
                crowd_index = 4
                crowd_description = "Busy"
            elif avg_wait <= 50:
                crowd_index = 5
                crowd_description = "Very Busy"
            elif avg_wait <= 70:
                crowd_index = 6
                crowd_description = "Packed"
            else:
                crowd_index = 7
                crowd_description = "Extremely Packed"
            
            return {
                "park_id": park_id,
                "date": target_date.isoformat(),
                "crowd_index": crowd_index,
                "crowd_description": crowd_description,
                "prediction_confidence": 0.8,  # Higher confidence with real data
                "peak_times": ["11:00 AM - 2:00 PM", "4:00 PM - 6:00 PM"],
                "best_visit_times": ["9:00 AM - 11:00 AM", "7:00 PM - 9:00 PM"],
                "estimated_wait_multiplier": 1.0 + (crowd_index - 4) * 0.15,
                "base_stats": {
                    "average_wait": avg_wait,
                    "max_wait": max_wait,
                    "open_attractions": wait_data["summary"]["open_attractions"]
                },
                "source": "waittimes-app-real-derived"
            }
            
        except Exception as e:
            logger.error(f"Error generating crowd predictions: {e}")
            return None
    
    async def optimize_park_plan(self, park_id: str, selected_attractions: List[str], 
                                visit_date: date, arrival_time: str = "09:00") -> Dict[str, Any]:
        """Generate optimized touring plan using real WaitTimesApp data"""
        try:
            wait_data = await self.get_live_wait_times(park_id)
            crowd_data = await self.get_crowd_predictions(park_id, visit_date)
            
            if not wait_data or wait_data.get("error"):
                return {"error": "Unable to fetch wait times data"}
            
            # Filter selected attractions
            all_attractions = wait_data["attractions"]
            selected_attraction_objects = [
                attr for attr in all_attractions 
                if attr["id"] in selected_attractions and attr["is_open"]
            ]
            
            if not selected_attraction_objects:
                return {"error": "No valid attractions selected or all attractions are closed"}
            
            # Sort by wait time for efficient routing
            sorted_attractions = sorted(
                selected_attraction_objects,
                key=lambda x: x["wait_time"] if x["wait_time"] else 0
            )
            
            # Generate optimized plan
            optimized_plan = []
            current_time = datetime.strptime(arrival_time, "%H:%M").time()
            
            for i, attraction in enumerate(sorted_attractions):
                time_increment = timedelta(minutes=i * 45)  # 45 minutes per attraction
                visit_time = (datetime.combine(visit_date, current_time) + time_increment).time()
                
                tips = []
                if attraction["wait_time"] > 30:
                    tips.append("High wait time - consider visiting during off-peak hours")
                if attraction["status"] == "VIRTUAL_QUEUE":
                    tips.append("Virtual queue system available - book in advance")
                if attraction["wait_time"] <= 10:
                    tips.append("Low wait time - great time to visit!")
                
                optimized_plan.append({
                    "order": i + 1,
                    "attraction": {
                        "id": attraction["id"],
                        "name": attraction["name"],
                        "land": attraction["land"]
                    },
                    "recommended_time": visit_time.strftime("%I:%M %p"),
                    "estimated_wait": attraction["wait_time"],
                    "status": attraction["status"],
                    "tips": tips
                })
            
            crowd_info = crowd_data or {"crowd_index": 4, "crowd_description": "Moderate"}
            
            return {
                "park_id": park_id,
                "park_name": wait_data.get("park_name", "Unknown Park"),
                "visit_date": visit_date.isoformat(),
                "crowd_level": crowd_info["crowd_index"],
                "crowd_description": crowd_info["crowd_description"],
                "total_attractions": len(optimized_plan),
                "estimated_total_time": f"{len(optimized_plan) * 45} minutes",
                "plan": optimized_plan,
                "general_tips": [
                    f"Current crowd level: {crowd_info['crowd_description']}",
                    "Plan was optimized based on current wait times",
                    "Virtual queue attractions should be booked in advance",
                    "Data powered by WaitTimesApp (real-time API)"
                ],
                "data_source": "waittimes-app-real"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing park plan: {e}")
            return {"error": f"Failed to optimize park plan: {str(e)}"}
    
    def _get_timezone_for_country(self, country: str) -> str:
        """Get timezone for a country (basic mapping)"""
        timezone_map = {
            "Germany": "Europe/Berlin",
            "Netherlands": "Europe/Amsterdam", 
            "Great Britain": "Europe/London",
            "United Kingdom": "Europe/London",
            "France": "Europe/Paris",
            "United States": "America/New_York",
            "USA": "America/New_York"
        }
        return timezone_map.get(country, "UTC")
    
    async def _get_fallback_parks(self) -> List[Dict[str, Any]]:
        """Return a small set of fallback parks when API is unavailable"""
        return [
            {
                "id": "fallback_park_1",
                "uuid": "fallback-uuid-1",
                "name": "Sample European Park",
                "country": "Germany",
                "timezone": "Europe/Berlin",
                "coordinates": {"latitude": None, "longitude": None},
                "source": "waittimes-app-fallback"
            }
        ]
    
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