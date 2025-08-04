"""
Enhanced Theme Park Service using Queue-Times.com and WaitTimesApp
Replaces thrill-data.com with multiple data sources for better coverage
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

# Updated Theme Park Service with Queue-Times.com and WaitTimesApp integration

class EnhancedThemeParkService:
    """Enhanced service combining Queue-Times.com and WaitTimesApp data"""
    
    def __init__(self):
        # Queue-Times.com configuration (free API)
        self.queue_times_base_url = "https://queue-times.com"
        self.queue_times_timeout = 30
        
        # WaitTimesApp configuration
        self.wait_times_app_base_url = "https://api.wartezeiten.app"
        self.wait_times_app_timeout = 30
        
        self.session = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(30),
            headers={'User-Agent': 'Dream-Travels/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def get_available_parks(self) -> Dict[str, Any]:
        """Get all available theme parks from both APIs"""
        parks_data = {
            "parks": [],
            "sources": [],
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Fetch from Queue-Times.com
        try:
            queue_times_parks = await self._fetch_queue_times_parks()
            parks_data["parks"].extend(queue_times_parks)
            parks_data["sources"].append("queue-times.com")
            logger.info(f"Fetched {len(queue_times_parks)} parks from Queue-Times.com")
        except Exception as e:
            logger.warning(f"Failed to fetch from Queue-Times.com: {e}")
        
        # Fetch from WaitTimesApp (if available)
        try:
            wait_times_parks = await self._fetch_wait_times_app_parks()
            parks_data["parks"].extend(wait_times_parks)
            parks_data["sources"].append("waittimes-app")
            logger.info(f"Fetched {len(wait_times_parks)} additional parks from WaitTimesApp")
        except Exception as e:
            logger.warning(f"Failed to fetch from WaitTimesApp: {e}")
        
        # Remove duplicates based on park name and location
        parks_data["parks"] = self._deduplicate_parks(parks_data["parks"])
        
        return parks_data
    
    async def _fetch_queue_times_parks(self) -> List[Dict[str, Any]]:
        """Fetch parks from Queue-Times.com API"""
        parks = []
        
        try:
            response = await self.session.get(f"{self.queue_times_base_url}/parks.json")
            response.raise_for_status()
            data = response.json()
            
            for company in data:
                company_name = company.get("name", "Unknown")
                
                for park_data in company.get("parks", []):
                    park = {
                        "id": f"qt_{park_data['id']}",  # Prefix to avoid ID conflicts
                        "name": park_data.get("name", "Unknown Park"),
                        "company": company_name,
                        "country": park_data.get("country", "Unknown"),
                        "continent": park_data.get("continent", "Unknown"),
                        "latitude": float(park_data.get("latitude", 0)) if park_data.get("latitude") else None,
                        "longitude": float(park_data.get("longitude", 0)) if park_data.get("longitude") else None,
                        "timezone": park_data.get("timezone", "UTC"),
                        "source": "queue-times.com",
                        "supported_features": ["wait_times", "park_status"],
                        "last_updated": datetime.utcnow().isoformat()
                    }
                    parks.append(park)
                    
        except Exception as e:
            logger.error(f"Error fetching Queue-Times parks: {e}")
            raise
            
        return parks
    
    async def _fetch_wait_times_app_parks(self) -> List[Dict[str, Any]]:
        """Fetch parks from WaitTimesApp API"""
        parks = []
        
        try:
            # Note: WaitTimesApp API structure may vary - this is a general implementation
            response = await self.session.get(f"{self.wait_times_app_base_url}/parks")
            response.raise_for_status()
            data = response.json()
            
            parks_list = data.get("parks", []) if isinstance(data, dict) else data
            
            for park_data in parks_list:
                park = {
                    "id": f"wta_{park_data.get('id', 'unknown')}",  # Prefix to avoid ID conflicts
                    "name": park_data.get("name", "Unknown Park"),
                    "company": park_data.get("operator", "Independent"),
                    "country": park_data.get("country", "Unknown"),
                    "continent": self._determine_continent_from_country(park_data.get("country", "")),
                    "latitude": park_data.get("latitude"),
                    "longitude": park_data.get("longitude"),
                    "timezone": park_data.get("timezone", "UTC"),
                    "source": "waittimes-app",
                    "supported_features": ["wait_times", "attraction_details"],
                    "last_updated": datetime.utcnow().isoformat()
                }
                parks.append(park)
                
        except Exception as e:
            logger.error(f"Error fetching WaitTimesApp parks: {e}")
            # Don't raise - this is a fallback API
            
        return parks
    
    async def get_park_wait_times(self, park_id: str) -> Dict[str, Any]:
        """Get current wait times for a specific park"""
        
        # Determine source from park ID prefix
        if park_id.startswith("qt_"):
            return await self._get_queue_times_wait_times(park_id[3:])  # Remove prefix
        elif park_id.startswith("wta_"):
            return await self._get_wait_times_app_wait_times(park_id[4:])  # Remove prefix
        else:
            # Try both sources
            try:
                return await self._get_queue_times_wait_times(park_id)
            except:
                return await self._get_wait_times_app_wait_times(park_id)
    
    async def _get_queue_times_wait_times(self, park_id: str) -> Dict[str, Any]:
        """Get wait times from Queue-Times.com"""
        try:
            response = await self.session.get(f"{self.queue_times_base_url}/parks/{park_id}/queue_times.json")
            response.raise_for_status()
            data = response.json()
            
            # Transform data to our format
            wait_times_data = {
                "park_id": f"qt_{park_id}",
                "park_name": data.get("name", f"Park {park_id}"),
                "source": "queue-times.com",
                "last_updated": datetime.utcnow().isoformat(),
                "attractions": []
            }
            
            for land in data.get("lands", []):
                land_name = land.get("name", "Unknown Area")
                
                for ride in land.get("rides", []):
                    attraction = {
                        "id": ride.get("id"),
                        "name": ride.get("name"),
                        "land": land_name,
                        "current_wait": ride.get("wait_time"),
                        "status": "operating" if ride.get("is_open", True) else "closed",
                        "last_updated": ride.get("last_updated"),
                        "supports_fastpass": ride.get("supports_fastpass", False),
                        "source": "queue-times.com"
                    }
                    wait_times_data["attractions"].append(attraction)
            
            # Calculate statistics
            operating_attractions = [a for a in wait_times_data["attractions"] if a["status"] == "operating"]
            wait_times = [a["current_wait"] for a in operating_attractions if a["current_wait"]]
            
            wait_times_data.update({
                "total_attractions": len(wait_times_data["attractions"]),
                "operating_attractions": len(operating_attractions),
                "average_wait_time": sum(wait_times) / len(wait_times) if wait_times else 0,
                "min_wait_time": min(wait_times) if wait_times else 0,
                "max_wait_time": max(wait_times) if wait_times else 0
            })
            
            return wait_times_data
            
        except Exception as e:
            logger.error(f"Error fetching Queue-Times wait times for park {park_id}: {e}")
            raise
    
    async def _get_wait_times_app_wait_times(self, park_id: str) -> Dict[str, Any]:
        """Get wait times from WaitTimesApp"""
        try:
            response = await self.session.get(f"{self.wait_times_app_base_url}/parks/{park_id}/waittimes")
            response.raise_for_status()
            data = response.json()
            
            # Transform data to our format
            wait_times_data = {
                "park_id": f"wta_{park_id}",
                "park_name": data.get("park_name", f"Park {park_id}"),
                "source": "waittimes-app",
                "last_updated": datetime.utcnow().isoformat(),
                "attractions": []
            }
            
            for attraction_data in data.get("attractions", []):
                attraction = {
                    "id": attraction_data.get("id"),
                    "name": attraction_data.get("name"),
                    "land": attraction_data.get("area", "Unknown Area"),
                    "current_wait": attraction_data.get("wait_time"),
                    "status": attraction_data.get("status", "unknown").lower(),
                    "last_updated": attraction_data.get("updated_at"),
                    "height_requirement": attraction_data.get("height_requirement"),
                    "supports_fastpass": attraction_data.get("has_fastpass", False),
                    "source": "waittimes-app"
                }
                wait_times_data["attractions"].append(attraction)
            
            # Calculate statistics
            operating_attractions = [a for a in wait_times_data["attractions"] if a["status"] == "operating"]
            wait_times = [a["current_wait"] for a in operating_attractions if a["current_wait"]]
            
            wait_times_data.update({
                "total_attractions": len(wait_times_data["attractions"]),
                "operating_attractions": len(operating_attractions),
                "average_wait_time": sum(wait_times) / len(wait_times) if wait_times else 0,
                "min_wait_time": min(wait_times) if wait_times else 0,
                "max_wait_time": max(wait_times) if wait_times else 0
            })
            
            return wait_times_data
            
        except Exception as e:
            logger.error(f"Error fetching WaitTimesApp wait times for park {park_id}: {e}")
            raise
    
    async def get_crowd_predictions(self, park_id: str, target_date: date) -> Dict[str, Any]:
        """Get crowd predictions for a specific park and date"""
        
        # Generate mock crowd predictions based on day of week and season
        # In a real implementation, this would use historical data analysis
        
        day_of_week = target_date.weekday()  # 0 = Monday, 6 = Sunday
        month = target_date.month
        
        # Base crowd level calculation
        if day_of_week in [5, 6]:  # Weekend
            base_crowd = 7
        elif day_of_week in [0, 4]:  # Monday, Friday
            base_crowd = 5
        else:  # Tuesday, Wednesday, Thursday
            base_crowd = 4
        
        # Seasonal adjustments
        if month in [6, 7, 8]:  # Summer
            base_crowd += 2
        elif month in [11, 12]:  # Holiday season
            base_crowd += 1
        elif month in [3, 4]:  # Spring break
            base_crowd += 1
        
        # Cap at 10
        crowd_level = min(base_crowd, 10)
        
        # Generate recommendations
        if crowd_level <= 3:
            crowd_description = "Light Crowds"
            recommendations = ["Great day to visit!", "Most attractions will have short waits"]
        elif crowd_level <= 6:
            crowd_description = "Moderate Crowds"
            recommendations = ["Arrive early for popular attractions", "Consider FastPass for busy rides"]
        else:
            crowd_description = "Heavy Crowds"
            recommendations = ["Arrive at park opening", "FastPass strongly recommended", "Consider visiting during parades"]
        
        return {
            "park_id": park_id,
            "date": target_date.isoformat(),
            "crowd_level": crowd_level,
            "crowd_description": crowd_description,
            "confidence": 0.75,  # Mock confidence level
            "peak_times": ["11:00 AM - 2:00 PM", "4:00 PM - 7:00 PM"],
            "best_times": ["8:00 AM - 10:00 AM", "8:00 PM - Close"],
            "recommendations": recommendations,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def optimize_park_plan(self, park_id: str, selected_attractions: List[str], 
                                visit_date: date, arrival_time: str = "08:00") -> Dict[str, Any]:
        """Generate optimized touring plan"""
        
        # Get current wait times for the park
        wait_times_data = await self.get_park_wait_times(park_id)
        crowd_prediction = await self.get_crowd_predictions(park_id, visit_date)
        
        # Filter attractions based on selection
        available_attractions = {
            attr["id"]: attr for attr in wait_times_data["attractions"]
            if str(attr["id"]) in [str(s) for s in selected_attractions]
        }
        
        if not available_attractions:
            raise ValueError("No valid attractions found for the selected IDs")
        
        # Sort attractions by current wait time (shortest first for morning strategy)
        sorted_attractions = sorted(
            available_attractions.values(),
            key=lambda x: x.get("current_wait", 999) if x.get("current_wait") else 999
        )
        
        # Generate optimized plan
        plan = []
        current_time = datetime.strptime(arrival_time, "%H:%M").time()
        
        for i, attraction in enumerate(sorted_attractions):
            # Estimate visit time (wait + ride + walk time)
            wait_time = attraction.get("current_wait", 30)
            ride_time = 10  # Estimated ride duration
            walk_time = 5   # Time to walk to next attraction
            
            total_time = wait_time + ride_time + walk_time
            
            # Calculate recommended time
            visit_datetime = datetime.combine(visit_date, current_time) + timedelta(minutes=i * 45)
            recommended_time = visit_datetime.time()
            
            # Generate tips based on attraction and crowd data
            tips = []
            if attraction.get("supports_fastpass"):
                tips.append("FastPass available - highly recommended!")
            if crowd_prediction["crowd_level"] >= 7:
                tips.append("Very busy day - arrive early at this attraction")
            if attraction.get("height_requirement"):
                tips.append(f"Height requirement: {attraction['height_requirement']}cm")
            
            plan_item = {
                "order": i + 1,
                "attraction": {
                    "id": attraction["id"],
                    "name": attraction["name"],
                    "land": attraction.get("land", "Unknown")
                },
                "recommended_time": recommended_time.strftime("%I:%M %p"),
                "estimated_wait": wait_time,
                "estimated_total_time": f"{total_time} minutes",
                "tips": tips
            }
            plan.append(plan_item)
        
        return {
            "park_id": park_id,
            "park_name": wait_times_data["park_name"],
            "visit_date": visit_date.isoformat(),
            "arrival_time": arrival_time,
            "crowd_level": crowd_prediction["crowd_level"],
            "crowd_description": crowd_prediction["crowd_description"],
            "total_attractions": len(plan),
            "estimated_total_time": f"{len(plan) * 45} minutes",
            "plan": plan,
            "general_tips": crowd_prediction["recommendations"] + [
                "Download the park's official app for real-time updates",
                "Stay hydrated and take breaks between attractions",
                "Check show schedules for entertainment options"
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _deduplicate_parks(self, parks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate parks based on name and location"""
        unique_parks = []
        seen_parks = set()
        
        for park in parks:
            # Create a unique identifier based on name and location
            identifier = f"{park['name'].lower()}_{park.get('country', '').lower()}"
            
            if identifier not in seen_parks:
                unique_parks.append(park)
                seen_parks.add(identifier)
        
        return unique_parks
    
    def _determine_continent_from_country(self, country: str) -> str:
        """Determine continent from country name"""
        continent_map = {
            "united states": "North America",
            "canada": "North America",
            "mexico": "North America",
            "france": "Europe",
            "germany": "Europe",
            "united kingdom": "Europe",
            "spain": "Europe",
            "italy": "Europe",
            "netherlands": "Europe",
            "japan": "Asia",
            "china": "Asia",
            "singapore": "Asia",
            "australia": "Australia/Oceania",
            "new zealand": "Australia/Oceania",
            "brazil": "South America",
            "argentina": "South America"
        }
        
        return continent_map.get(country.lower(), "Unknown")