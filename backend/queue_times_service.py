"""
Queue Times API Service
Replaces thrill-data.com with queue-times.com API for theme park wait times
Provides real-time wait times for 80+ theme parks worldwide
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

# Queue Times API Configuration
QUEUE_TIMES_BASE_URL = "https://queue-times.com"

class QueueTimesAttraction(BaseModel):
    id: int
    name: str
    is_open: bool
    wait_time: Optional[int] = None
    last_updated: Optional[str] = None
    active: bool = True

class QueueTimesLand(BaseModel):
    id: int
    name: str
    rides: List[QueueTimesAttraction]

class QueueTimesPark(BaseModel):
    id: int
    name: str
    country: str
    continent: str
    timezone: str
    is_open: bool
    lands: List[QueueTimesLand] = []

class QueueTimesService:
    """Service for integrating with Queue Times API (queue-times.com)"""
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.queue_times_db
        self.client = httpx.AsyncClient(timeout=30.0)
        self.base_url = QUEUE_TIMES_BASE_URL
        
        # Park ID mapping for common parks
        self.park_mappings = {
            "wdw_magic_kingdom": 6,  # Disney's Magic Kingdom
            "wdw_epcot": 8,          # EPCOT
            "wdw_hollywood_studios": 7,  # Disney's Hollywood Studios
            "wdw_animal_kingdom": 9,  # Disney's Animal Kingdom
            "universal_studios_orlando": 3,  # Universal Studios Florida
            "islands_of_adventure": 4,       # Islands of Adventure
            "disneyland_california": 1,      # Disneyland Park
            "california_adventure": 2        # Disney California Adventure
        }
        
    async def get_available_parks(self) -> List[Dict[str, Any]]:
        """Get list of all available theme parks from Queue Times"""
        try:
            logger.info("Fetching available parks from Queue Times")
            
            # Check cache first
            cache_key = "queue_times_parks_list"
            cached_parks = await self._get_cached_data(cache_key)
            if cached_parks:
                return cached_parks
            
            response = await self.client.get(f"{self.base_url}/parks.json")
            response.raise_for_status()
            
            parks_data = response.json()
            processed_parks = []
            
            # Process the nested structure: companies -> parks
            for company in parks_data:
                company_name = company.get("name", "Unknown Company")
                parks = company.get("parks", [])
                
                for park in parks:
                    processed_park = {
                        "id": str(park.get("id", "")),
                        "name": park.get("name", "Unknown Park"),
                        "country": park.get("country", ""),
                        "continent": park.get("continent", ""),
                        "timezone": park.get("timezone", "UTC"),
                        "company": company_name,
                        "coordinates": {
                            "latitude": park.get("latitude"),
                            "longitude": park.get("longitude")
                        },
                        "source": "queue-times"
                    }
                    processed_parks.append(processed_park)
            
            # Cache for 4 hours
            await self._cache_data(cache_key, processed_parks, ttl_hours=4)
            
            logger.info(f"Retrieved {len(processed_parks)} parks from Queue Times")
            return processed_parks
            
        except Exception as e:
            logger.error(f"Error fetching parks from Queue Times: {e}")
            return []
    
    async def get_park_by_id(self, park_id: str) -> Optional[Dict[str, Any]]:
        """Get specific park information by ID"""
        try:
            # Convert internal park ID to Queue Times ID if needed
            qt_park_id = self.park_mappings.get(park_id, park_id)
            
            all_parks = await self.get_available_parks()
            for park in all_parks:
                if park["id"] == str(qt_park_id):
                    return park
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting park {park_id}: {e}")
            return None
    
    async def get_live_wait_times(self, park_id: str) -> Optional[Dict[str, Any]]:
        """Get current wait times for all attractions in a park"""
        try:
            # Convert internal park ID to Queue Times ID if needed
            qt_park_id = self.park_mappings.get(park_id, park_id)
            
            logger.info(f"Fetching wait times for park {qt_park_id} from Queue Times")
            
            # Check cache first (5 minute cache for real-time data)
            cache_key = f"queue_times_wait_{qt_park_id}"
            cached_data = await self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            response = await self.client.get(f"{self.base_url}/parks/{qt_park_id}/queue_times.json")
            response.raise_for_status()
            
            wait_data = response.json()
            
            # Process the data structure
            processed_data = {
                "park_id": park_id,
                "queue_times_id": qt_park_id,
                "last_updated": datetime.utcnow().isoformat(),
                "attractions": [],
                "lands": [],
                "summary": {
                    "total_attractions": 0,
                    "open_attractions": 0,
                    "average_wait": 0,
                    "max_wait": 0
                },
                "source": "queue-times"
            }
            
            total_wait = 0
            wait_count = 0
            max_wait = 0
            
            # Process lands and rides
            lands = wait_data.get("lands", [])
            for land in lands:
                land_info = {
                    "id": land.get("id"),
                    "name": land.get("name", "Unknown Land"),
                    "attractions": []
                }
                
                rides = land.get("rides", [])
                for ride in rides:
                    wait_time = ride.get("wait_time", 0)
                    is_open = ride.get("is_open", False)
                    
                    attraction = {
                        "id": str(ride.get("id", "")),
                        "name": ride.get("name", "Unknown Attraction"),
                        "wait_time": wait_time if wait_time is not None else 0,
                        "is_open": is_open,
                        "status": "OPERATIONAL" if is_open else "CLOSED",
                        "last_updated": ride.get("last_updated", processed_data["last_updated"]),
                        "land": land_info["name"],
                        "land_id": land_info["id"],
                        "active": ride.get("active", True),
                        "thrill_level": "UNKNOWN",  # Queue Times doesn't provide this
                        "height_requirement": None,  # Queue Times doesn't provide this
                        "fastpass_available": False  # Queue Times doesn't provide this
                    }
                    
                    processed_data["attractions"].append(attraction)
                    land_info["attractions"].append(attraction)
                    
                    # Update summary statistics
                    processed_data["summary"]["total_attractions"] += 1
                    if is_open:
                        processed_data["summary"]["open_attractions"] += 1
                        if wait_time and wait_time > 0:
                            total_wait += wait_time
                            wait_count += 1
                            max_wait = max(max_wait, wait_time)
                
                if land_info["attractions"]:  # Only add lands with attractions
                    processed_data["lands"].append(land_info)
            
            # Calculate average wait time
            if wait_count > 0:
                processed_data["summary"]["average_wait"] = round(total_wait / wait_count, 1)
            processed_data["summary"]["max_wait"] = max_wait
            
            # Cache for 5 minutes
            await self._cache_data(cache_key, processed_data, ttl_minutes=5)
            
            logger.info(f"Retrieved wait times for {processed_data['summary']['total_attractions']} attractions")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error fetching wait times for park {park_id}: {e}")
            return None
    
    async def get_crowd_predictions(self, park_id: str, target_date: date) -> Optional[Dict[str, Any]]:
        """Get crowd level predictions - derived from wait times since Queue Times doesn't provide explicit crowd data"""
        try:
            wait_data = await self.get_live_wait_times(park_id)
            if not wait_data:
                return None
            
            # Calculate crowd level based on average wait times
            avg_wait = wait_data["summary"]["average_wait"]
            max_wait = wait_data["summary"]["max_wait"]
            open_attractions = wait_data["summary"]["open_attractions"]
            
            # Determine crowd level (1-10 scale) based on wait times
            if avg_wait <= 10:
                crowd_index = 1
                crowd_description = "Ghost Town"
            elif avg_wait <= 20:
                crowd_index = 2
                crowd_description = "Very Light"
            elif avg_wait <= 30:
                crowd_index = 3
                crowd_description = "Light"
            elif avg_wait <= 45:
                crowd_index = 4
                crowd_description = "Moderate"
            elif avg_wait <= 60:
                crowd_index = 5
                crowd_description = "Busy"
            elif avg_wait <= 75:
                crowd_index = 6
                crowd_description = "Very Busy"
            elif avg_wait <= 90:
                crowd_index = 7
                crowd_description = "Packed"
            elif avg_wait <= 120:
                crowd_index = 8
                crowd_description = "Extremely Packed"
            else:
                crowd_index = 9
                crowd_description = "Avoid at All Costs"
            
            # Generate recommendations based on crowd level
            if crowd_index <= 3:
                peak_times = ["No significant peak times"]
                best_visit_times = ["Any time is good"]
            elif crowd_index <= 5:
                peak_times = ["12:00 PM - 3:00 PM"]
                best_visit_times = ["8:00 AM - 11:00 AM", "6:00 PM - 9:00 PM"]
            else:
                peak_times = ["11:00 AM - 2:00 PM", "4:00 PM - 7:00 PM"]
                best_visit_times = ["8:00 AM - 10:00 AM", "8:00 PM - 10:00 PM"]
            
            return {
                "park_id": park_id,
                "date": target_date.isoformat(),
                "crowd_index": crowd_index,
                "crowd_description": crowd_description,
                "prediction_confidence": 0.7,  # Lower confidence since derived from wait times
                "peak_times": peak_times,
                "best_visit_times": best_visit_times,
                "estimated_wait_multiplier": self._get_wait_multiplier(crowd_index),
                "data_source": "derived_from_queue_times",
                "base_stats": {
                    "average_wait": avg_wait,
                    "max_wait": max_wait,
                    "open_attractions": open_attractions
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating crowd predictions for park {park_id}: {e}")
            return None
    
    async def get_historical_wait_times(self, park_id: str, target_date: date) -> Optional[Dict[str, Any]]:
        """Get historical wait times (Queue Times may have limited historical data)"""
        try:
            # Queue Times doesn't explicitly provide historical API, but we can try
            # This is a placeholder implementation
            logger.info(f"Historical data requested for {park_id} on {target_date}")
            
            # For now, return current data as a proxy
            current_data = await self.get_live_wait_times(park_id)
            if current_data:
                return {
                    "park_id": park_id,
                    "date": target_date.isoformat(),
                    "note": "Historical data limited - showing current structure",
                    "attractions": current_data["attractions"],
                    "source": "queue-times"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    async def optimize_park_plan(self, park_id: str, selected_attractions: List[str], 
                                visit_date: date, arrival_time: str = "08:00") -> Dict[str, Any]:
        """Generate optimized touring plan using Queue Times data"""
        try:
            wait_data = await self.get_live_wait_times(park_id)
            crowd_data = await self.get_crowd_predictions(park_id, visit_date)
            
            if not wait_data or not crowd_data:
                return None
            
            # Filter selected attractions
            all_attractions = wait_data["attractions"]
            selected_attraction_objects = [
                attr for attr in all_attractions 
                if attr["id"] in selected_attractions and attr["is_open"]
            ]
            
            if not selected_attraction_objects:
                return {
                    "error": "No valid attractions selected or all attractions are closed"
                }
            
            # Sort by current wait time (lowest first for efficiency)
            sorted_attractions = sorted(
                selected_attraction_objects,
                key=lambda x: x["wait_time"] if x["wait_time"] else 999
            )
            
            optimized_plan = []
            current_time = datetime.strptime(arrival_time, "%H:%M").time()
            
            for i, attraction in enumerate(sorted_attractions):
                # Calculate visit time
                time_increment = timedelta(minutes=i * 45)  # 45 minutes per attraction average
                visit_time = (datetime.combine(visit_date, current_time) + time_increment).time()
                
                # Generate tips based on wait time and crowd level
                tips = []
                if attraction["wait_time"] > 60:
                    tips.append("High wait time - consider visiting during off-peak hours")
                if crowd_data["crowd_index"] >= 7:
                    tips.append("Very crowded day - arrive early for shorter waits")
                tips.append(f"Located in {attraction['land']}")
                
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
            
            return {
                "park_id": park_id,
                "visit_date": visit_date.isoformat(),
                "crowd_level": crowd_data["crowd_index"],
                "crowd_description": crowd_data["crowd_description"],
                "total_attractions": len(optimized_plan),
                "estimated_total_time": f"{len(optimized_plan) * 45} minutes",
                "plan": optimized_plan,
                "general_tips": [
                    f"Current crowd level: {crowd_data['crowd_description']}",
                    f"Best times to visit: {', '.join(crowd_data['best_visit_times'])}",
                    f"Avoid peak times: {', '.join(crowd_data['peak_times'])}",
                    "Data powered by queue-times.com - updates every 5 minutes"
                ],
                "data_source": "queue-times"
            }
            
        except Exception as e:
            logger.error(f"Error optimizing park plan: {e}")
            return None
    
    def _get_wait_multiplier(self, crowd_index: int) -> float:
        """Get wait time multiplier based on crowd level"""
        multipliers = {
            1: 0.3, 2: 0.5, 3: 0.7, 4: 0.9, 5: 1.0,
            6: 1.3, 7: 1.6, 8: 2.0, 9: 2.5, 10: 3.0
        }
        return multipliers.get(crowd_index, 1.0)
    
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