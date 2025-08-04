"""
Travel Blog Scraper Service
Scrapes data from popular travel blogs and tourism sites to replace Google Places API
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
import json
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class ScrapedActivity:
    name: str
    description: str
    location: str
    category: str
    source_url: str
    estimated_duration: str = "2-3 hours"
    best_time: str = "Anytime"
    price_range: str = "Free"
    coordinates: Optional[Dict[str, float]] = None
    image_url: Optional[str] = None
    
class TravelBlogScraper:
    """Main scraper class for extracting travel recommendations from blogs"""
    
    def __init__(self):
        self.session = None
        self.scraped_cache = {}
        self.rate_limit_delay = 2  # seconds between requests
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def scrape_destination_activities(self, destination: str, interests: List[str]) -> List[ScrapedActivity]:
        """Main method to scrape activities for a destination"""
        activities = []
        
        # Define target sites and their scraping strategies
        scrapers = [
            self._scrape_lonely_planet,
            self._scrape_atlas_obscura,
            self._scrape_timeout,
            self._scrape_culture_trip,
            self._scrape_tripadvisor_blog
        ]
        
        for scraper in scrapers:
            try:
                scraped_activities = await scraper(destination, interests)
                activities.extend(scraped_activities)
                await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
            except Exception as e:
                logger.warning(f"Failed to scrape from {scraper.__name__}: {e}")
                continue
        
        # Remove duplicates and return
        return self._deduplicate_activities(activities)
    
    async def _scrape_lonely_planet(self, destination: str, interests: List[str]) -> List[ScrapedActivity]:
        """Scrape Lonely Planet for destination recommendations"""
        activities = []
        
        # Search for destination-specific Lonely Planet pages
        search_query = f"{destination} attractions things to do"
        search_url = f"https://www.lonelyplanet.com/search?q={search_query.replace(' ', '+')}"
        
        try:
            response = await self.session.get(search_url)
            if response.status_code != 200:
                return activities
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for attraction articles and recommendations
            article_links = soup.find_all('a', href=re.compile(r'/[^/]+/attractions/'))
            
            for link in article_links[:5]:  # Limit to avoid overwhelming
                article_url = urljoin('https://www.lonelyplanet.com', link.get('href'))
                article_activities = await self._scrape_lonely_planet_article(article_url)
                activities.extend(article_activities)
                await asyncio.sleep(self.rate_limit_delay)
                
        except Exception as e:
            logger.error(f"Error scraping Lonely Planet: {e}")
            
        return activities
    
    async def _scrape_lonely_planet_article(self, url: str) -> List[ScrapedActivity]:
        """Scrape individual Lonely Planet article for activities"""
        activities = []
        
        try:
            response = await self.session.get(url)
            if response.status_code != 200:
                return activities
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract attraction information
            attractions = soup.find_all(['div', 'section'], class_=re.compile(r'attraction|place|poi'))
            
            for attraction in attractions:
                name_elem = attraction.find(['h1', 'h2', 'h3'], string=True)
                desc_elem = attraction.find('p')
                
                if name_elem and desc_elem:
                    activity = ScrapedActivity(
                        name=name_elem.get_text().strip(),
                        description=desc_elem.get_text().strip()[:500] + "...",
                        location=self._extract_location_from_text(desc_elem.get_text()),
                        category=self._categorize_activity(name_elem.get_text(), desc_elem.get_text()),
                        source_url=url,
                        estimated_duration="2-3 hours",
                        best_time="Check opening hours"
                    )
                    activities.append(activity)
                    
        except Exception as e:
            logger.warning(f"Error scraping Lonely Planet article {url}: {e}")
            
        return activities
    
    async def _scrape_atlas_obscura(self, destination: str, interests: List[str]) -> List[ScrapedActivity]:
        """Scrape Atlas Obscura for unique and unusual attractions"""
        activities = []
        
        try:
            # Atlas Obscura search
            search_url = f"https://www.atlasobscura.com/search?q={destination.replace(' ', '+')}"
            response = await self.session.get(search_url)
            
            if response.status_code != 200:
                return activities
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find place cards
            place_cards = soup.find_all('div', class_=re.compile(r'place-card|item-card'))
            
            for card in place_cards[:10]:  # Limit results
                title_elem = card.find(['h3', 'h4', 'a'], class_=re.compile(r'title|name'))
                desc_elem = card.find('p', class_=re.compile(r'description|subtitle'))
                
                if title_elem and desc_elem:
                    activity = ScrapedActivity(
                        name=title_elem.get_text().strip(),
                        description=desc_elem.get_text().strip(),
                        location=destination,
                        category="hidden gems",
                        source_url="https://www.atlasobscura.com",
                        estimated_duration="1-2 hours",
                        best_time="Varies by location"
                    )
                    activities.append(activity)
                    
        except Exception as e:
            logger.warning(f"Error scraping Atlas Obscura: {e}")
            
        return activities
    
    async def _scrape_timeout(self, destination: str, interests: List[str]) -> List[ScrapedActivity]:
        """Scrape TimeOut for local recommendations"""
        activities = []
        
        try:
            # TimeOut city guides
            city_slug = destination.lower().replace(' ', '-').replace(',', '')
            timeout_url = f"https://www.timeout.com/{city_slug}/things-to-do"
            
            response = await self.session.get(timeout_url)
            if response.status_code != 200:
                return activities
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find recommendation sections
            recommendations = soup.find_all(['article', 'div'], class_=re.compile(r'listing|recommendation|card'))
            
            for rec in recommendations[:8]:
                title_elem = rec.find(['h2', 'h3', 'h4'])
                desc_elem = rec.find('p')
                
                if title_elem and desc_elem:
                    activity = ScrapedActivity(
                        name=title_elem.get_text().strip(),
                        description=desc_elem.get_text().strip()[:400] + "...",
                        location=destination,
                        category=self._categorize_timeout_activity(title_elem.get_text()),
                        source_url=timeout_url,
                        estimated_duration="2-4 hours",
                        best_time="Check local hours"
                    )
                    activities.append(activity)
                    
        except Exception as e:
            logger.warning(f"Error scraping TimeOut: {e}")
            
        return activities
    
    async def _scrape_culture_trip(self, destination: str, interests: List[str]) -> List[ScrapedActivity]:
        """Scrape Culture Trip for cultural activities"""
        activities = []
        
        try:
            search_url = f"https://theculturetrip.com/search?q={destination.replace(' ', '+')}"
            response = await self.session.get(search_url)
            
            if response.status_code != 200:
                return activities
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find article cards
            article_cards = soup.find_all('article', class_=re.compile(r'card|post'))
            
            for card in article_cards[:6]:
                title_elem = card.find(['h2', 'h3'])
                desc_elem = card.find('p')
                
                if title_elem and desc_elem:
                    activity = ScrapedActivity(
                        name=title_elem.get_text().strip(),
                        description=desc_elem.get_text().strip(),
                        location=destination,
                        category="cultural experiences",
                        source_url="https://theculturetrip.com",
                        estimated_duration="2-3 hours",
                        best_time="Daytime recommended"
                    )
                    activities.append(activity)
                    
        except Exception as e:
            logger.warning(f"Error scraping Culture Trip: {e}")
            
        return activities
    
    async def _scrape_tripadvisor_blog(self, destination: str, interests: List[str]) -> List[ScrapedActivity]:
        """Scrape TripAdvisor blog posts for recommendations"""
        activities = []
        
        try:
            # TripAdvisor blog search
            search_url = f"https://blog.tripadvisor.com/?s={destination.replace(' ', '+')}"
            response = await self.session.get(search_url)
            
            if response.status_code != 200:
                return activities
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find blog post excerpts
            post_excerpts = soup.find_all('div', class_=re.compile(r'post|entry|excerpt'))
            
            for excerpt in post_excerpts[:5]:
                title_elem = excerpt.find(['h2', 'h3'])
                content_elem = excerpt.find('p')
                
                if title_elem and content_elem:
                    # Extract specific recommendations from blog content
                    recommendations = self._extract_recommendations_from_text(content_elem.get_text())
                    
                    for rec in recommendations:
                        activity = ScrapedActivity(
                            name=rec['name'],
                            description=rec['description'],
                            location=destination,
                            category=rec['category'],
                            source_url="https://blog.tripadvisor.com",
                            estimated_duration="2-3 hours",
                            best_time="Varies"
                        )
                        activities.append(activity)
                        
        except Exception as e:
            logger.warning(f"Error scraping TripAdvisor blog: {e}")
            
        return activities
    
    def _extract_location_from_text(self, text: str) -> str:
        """Extract location information from descriptive text"""
        # Simple regex patterns for common location indicators
        location_patterns = [
            r'located in ([^,.\n]+)',
            r'situated in ([^,.\n]+)',
            r'found in ([^,.\n]+)',
            r'in the ([^,.\n]+) district',
            r'near ([^,.\n]+)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        return "Location details in description"
    
    def _categorize_activity(self, name: str, description: str) -> str:
        """Categorize activity based on name and description"""
        text = (name + " " + description).lower()
        
        # Define category keywords
        categories = {
            "museums": ["museum", "gallery", "exhibition", "art", "history", "science"],
            "historic landmarks": ["historic", "monument", "castle", "palace", "church", "cathedral", "temple"],
            "outdoor activities": ["park", "garden", "hike", "trail", "outdoor", "nature", "beach"],
            "dining hot spots": ["restaurant", "food", "market", "cafe", "dining", "culinary"],
            "nightlife": ["bar", "club", "nightlife", "entertainment", "music", "theater"],
            "shopping": ["shop", "market", "mall", "boutique", "store"],
            "family friendly": ["family", "children", "kids", "playground", "zoo", "aquarium"],
            "cultural experiences": ["culture", "tradition", "local", "authentic", "festival", "ceremony"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
                
        return "attractions"
    
    def _categorize_timeout_activity(self, title: str) -> str:
        """Specific categorization for TimeOut content"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ["restaurant", "eat", "food", "drink", "bar"]):
            return "dining hot spots"
        elif any(word in title_lower for word in ["museum", "gallery", "art"]):
            return "museums"
        elif any(word in title_lower for word in ["park", "outdoor", "garden"]):
            return "outdoor activities"
        elif any(word in title_lower for word in ["show", "theater", "music", "nightlife"]):
            return "nightlife"
        else:
            return "cultural experiences"
    
    def _extract_recommendations_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract specific recommendations from blog text"""
        recommendations = []
        
        # Simple pattern matching for recommendations
        # Look for numbered lists or bullet points
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines or very short lines
            if len(line) < 20:
                continue
                
            # Look for recommendation patterns
            if any(starter in line.lower()[:50] for starter in ["visit", "see", "check out", "don't miss", "must-see"]):
                # Extract the main recommendation
                words = line.split()
                if len(words) >= 5:
                    name = " ".join(words[:4]).title()
                    description = line
                    category = self._categorize_activity(name, description)
                    
                    recommendations.append({
                        'name': name,
                        'description': description[:300] + "..." if len(description) > 300 else description,
                        'category': category
                    })
        
        return recommendations[:3]  # Limit to avoid overwhelming
    
    def _deduplicate_activities(self, activities: List[ScrapedActivity]) -> List[ScrapedActivity]:
        """Remove duplicate activities based on name similarity"""
        unique_activities = []
        seen_names = set()
        
        for activity in activities:
            # Normalize name for comparison
            normalized_name = re.sub(r'[^\w\s]', '', activity.name.lower()).strip()
            
            # Check for similarity with existing activities
            is_duplicate = False
            for seen_name in seen_names:
                if self._calculate_similarity(normalized_name, seen_name) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_activities.append(activity)
                seen_names.add(normalized_name)
        
        return unique_activities
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0.0
            
        # Simple Jaccard similarity
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

class BlogActivityService:
    """Service to manage scraped blog activities and integrate with the main app"""
    
    def __init__(self):
        self.scraper = TravelBlogScraper()
        self.activity_cache = {}
        self.cache_ttl = timedelta(hours=24)  # Cache for 24 hours
        
    async def get_activities_for_destination(self, destination: str, interests: List[str]) -> List[Dict[str, Any]]:
        """Get activities for a destination, using cache when possible"""
        cache_key = f"{destination}_{'+'.join(sorted(interests))}"
        
        # Check cache first
        if cache_key in self.activity_cache:
            cached_data = self.activity_cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < self.cache_ttl:
                logger.info(f"Returning cached activities for {destination}")
                return cached_data['activities']
        
        # Scrape fresh data
        async with self.scraper:
            scraped_activities = await self.scraper.scrape_destination_activities(destination, interests)
        
        # Convert to dict format for the main app
        activities = []
        for scraped_activity in scraped_activities:
            # Generate approximate coordinates for the destination
            coordinates = self._get_approximate_coordinates(destination)
            
            activity_dict = {
                "name": scraped_activity.name,
                "category": scraped_activity.category,
                "description": scraped_activity.description,
                "location": {
                    "lat": coordinates["lat"] + (hash(scraped_activity.name) % 1000 - 500) / 100000,  # Small random offset
                    "lng": coordinates["lng"] + (hash(scraped_activity.name) % 1000 - 500) / 100000
                },
                "address": scraped_activity.location,
                "estimated_duration": scraped_activity.estimated_duration,
                "best_time": scraped_activity.best_time,
                "source": "travel_blogs",
                "source_url": scraped_activity.source_url
            }
            activities.append(activity_dict)
        
        # Cache the results
        self.activity_cache[cache_key] = {
            'activities': activities,
            'timestamp': datetime.now()
        }
        
        logger.info(f"Scraped {len(activities)} activities for {destination}")
        return activities
    
    def _get_approximate_coordinates(self, destination: str) -> Dict[str, float]:
        """Get approximate coordinates for major destinations"""
        # Hardcoded coordinates for major destinations
        coords_map = {
            "london": {"lat": 51.5074, "lng": -0.1278},
            "paris": {"lat": 48.8566, "lng": 2.3522},
            "new york": {"lat": 40.7128, "lng": -74.0060},
            "tokyo": {"lat": 35.6762, "lng": 139.6503},
            "sydney": {"lat": -33.8688, "lng": 151.2093},
            "rome": {"lat": 41.9028, "lng": 12.4964},
            "barcelona": {"lat": 41.3851, "lng": 2.1734},
            "amsterdam": {"lat": 52.3676, "lng": 4.9041},
            "berlin": {"lat": 52.5200, "lng": 13.4050},
            "madrid": {"lat": 40.4168, "lng": -3.7038},
            "vienna": {"lat": 48.2082, "lng": 16.3738},
            "prague": {"lat": 50.0755, "lng": 14.4378},
            "budapest": {"lat": 47.4979, "lng": 19.0402},
            "lisbon": {"lat": 38.7223, "lng": -9.1393},
            "dublin": {"lat": 53.3498, "lng": -6.2603},
            "edinburgh": {"lat": 55.9533, "lng": -3.1883},
            "stockholm": {"lat": 59.3293, "lng": 18.0686},
            "copenhagen": {"lat": 55.6761, "lng": 12.5683},
            "oslo": {"lat": 59.9139, "lng": 10.7522},
            "helsinki": {"lat": 60.1699, "lng": 24.9384}
        }
        
        destination_lower = destination.lower().split(',')[0].strip()
        
        # Try exact match first
        if destination_lower in coords_map:
            return coords_map[destination_lower]
        
        # Try partial match
        for city, coords in coords_map.items():
            if city in destination_lower or destination_lower in city:
                return coords
        
        # Default to London if no match found
        return coords_map["london"]
    
    async def refresh_destination_cache(self, destination: str, interests: List[str]):
        """Force refresh of cached data for a destination"""
        cache_key = f"{destination}_{'+'.join(sorted(interests))}"
        if cache_key in self.activity_cache:
            del self.activity_cache[cache_key]
        
        # Fetch fresh data
        return await self.get_activities_for_destination(destination, interests)