"""
Travel Blog Scraping Service
Replaces Google Places API with data gathered from public travel blogs
Provides destination information, activities, and local insights
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib
import os
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

class TravelBlogService:
    """Service for scraping travel blog data to gather destination information"""
    
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client.travel_blogs_db
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        
        # Blog sources similar to the ones mentioned by user
        self.blog_sources = {
            "hawaii_vacation_guide": {
                "base_url": "https://thehawaiivacationguide.com",
                "sitemap_url": "https://thehawaiivacationguide.com/sitemap.xml",
                "focus_regions": ["hawaii", "pacific"],
                "specialties": ["beaches", "outdoor", "island_hopping"]
            },
            "awanderlustforlife": {
                "base_url": "https://www.awanderlustforlife.com", 
                "sitemap_url": "https://www.awanderlustforlife.com/sitemap.xml",
                "focus_regions": ["global"],
                "specialties": ["adventure", "photography", "solo_travel"]
            },
            "toeuropeandbeyond": {
                "base_url": "https://www.toeuropeandbeyond.com",
                "sitemap_url": "https://www.toeuropeandbeyond.com/sitemap.xml", 
                "focus_regions": ["europe", "asia"],
                "specialties": ["culture", "history", "food"]
            },
            "nomadic_matt": {
                "base_url": "https://www.nomadicmatt.com",
                "sitemap_url": "https://www.nomadicmatt.com/sitemap.xml",
                "focus_regions": ["global"],
                "specialties": ["budget_travel", "backpacking", "solo_travel"]
            }
        }
        
    async def scrape_destination_data(self, destination: str, interests: List[str]) -> Dict[str, Any]:
        """Scrape travel blog data for a specific destination"""
        logger.info(f"Scraping travel blog data for {destination}")
        
        # Check cache first
        cache_key = self._generate_cache_key(destination, interests)
        cached_data = await self._get_cached_data(cache_key)
        if cached_data:
            logger.info(f"Returning cached data for {destination}")
            return cached_data
        
        # Scrape from multiple blog sources
        scraped_data = {
            "destination": destination,
            "interests": interests,
            "activities": [],
            "restaurants": [],
            "accommodations": [],
            "local_tips": [],
            "best_time_to_visit": "",
            "budget_info": {},
            "safety_info": {},
            "sources": [],
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Search each blog source
        for blog_name, blog_config in self.blog_sources.items():
            try:
                blog_data = await self._scrape_single_blog(blog_name, blog_config, destination, interests)
                if blog_data:
                    scraped_data = self._merge_blog_data(scraped_data, blog_data, blog_name)
                    scraped_data["sources"].append(blog_name)
            except Exception as e:
                logger.error(f"Error scraping {blog_name}: {e}")
                continue
        
        # Cache the results
        await self._cache_data(cache_key, scraped_data)
        
        logger.info(f"Completed scraping for {destination}, found {len(scraped_data['activities'])} activities")
        return scraped_data
    
    async def _scrape_single_blog(self, blog_name: str, blog_config: Dict, destination: str, interests: List[str]) -> Optional[Dict[str, Any]]:
        """Scrape data from a single travel blog"""
        try:
            # Search for destination-related content
            search_urls = await self._find_destination_articles(blog_config, destination)
            
            if not search_urls:
                logger.info(f"No articles found for {destination} on {blog_name}")
                return None
            
            blog_data = {
                "activities": [],
                "restaurants": [],
                "accommodations": [],
                "local_tips": [],
                "budget_info": {},
                "safety_info": {}
            }
            
            # Process up to 5 most relevant articles
            for url in search_urls[:5]:
                try:
                    article_data = await self._scrape_article(url, destination, interests)
                    if article_data:
                        blog_data = self._merge_article_data(blog_data, article_data)
                except Exception as e:
                    logger.error(f"Error scraping article {url}: {e}")
                    continue
            
            return blog_data
            
        except Exception as e:
            logger.error(f"Error in _scrape_single_blog for {blog_name}: {e}")
            return None
    
    async def _find_destination_articles(self, blog_config: Dict, destination: str) -> List[str]:
        """Find articles related to a destination on a blog"""
        try:
            base_url = blog_config["base_url"]
            
            # Try multiple search approaches
            search_urls = []
            
            # Approach 1: Direct search URL patterns
            search_patterns = [
                f"{base_url}/search?q={destination.replace(' ', '+')}",
                f"{base_url}/?s={destination.replace(' ', '+')}",
                f"{base_url}/tag/{destination.lower().replace(' ', '-')}",
                f"{base_url}/category/{destination.lower().replace(' ', '-')}"
            ]
            
            for search_url in search_patterns:
                try:
                    response = await self.client.get(search_url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        article_links = self._extract_article_links(soup, base_url, destination)
                        search_urls.extend(article_links)
                        if len(search_urls) >= 10:  # Limit to prevent too many requests
                            break
                except Exception as e:
                    logger.debug(f"Search pattern failed for {search_url}: {e}")
                    continue
            
            # Approach 2: Sitemap crawling (if available)
            if not search_urls and blog_config.get("sitemap_url"):
                try:
                    sitemap_urls = await self._crawl_sitemap(blog_config["sitemap_url"], destination)
                    search_urls.extend(sitemap_urls)
                except Exception as e:
                    logger.debug(f"Sitemap crawling failed: {e}")
            
            return list(set(search_urls))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error finding destination articles: {e}")
            return []
    
    async def _crawl_sitemap(self, sitemap_url: str, destination: str) -> List[str]:
        """Crawl sitemap to find relevant URLs"""
        try:
            response = await self.client.get(sitemap_url)
            if response.status_code != 200:
                return []
            
            # Parse sitemap XML
            soup = BeautifulSoup(response.content, 'xml')
            urls = []
            
            destination_keywords = destination.lower().split()
            
            for loc in soup.find_all('loc'):
                url = loc.text.strip()
                url_lower = url.lower()
                
                # Check if URL contains destination keywords
                if any(keyword in url_lower for keyword in destination_keywords):
                    urls.append(url)
                    if len(urls) >= 10:  # Limit results
                        break
            
            return urls
            
        except Exception as e:
            logger.error(f"Error crawling sitemap {sitemap_url}: {e}")
            return []
    
    def _extract_article_links(self, soup: BeautifulSoup, base_url: str, destination: str) -> List[str]:
        """Extract article links from search results or category pages"""
        links = []
        destination_lower = destination.lower()
        
        # Common selectors for article links
        selectors = [
            'a[href*="' + destination_lower.replace(' ', '-') + '"]',
            '.post-title a', '.entry-title a', '.article-title a',
            'h2 a', 'h3 a', '.post a[href*="http"]'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    title = element.text.strip()
                    
                    if href and title:
                        # Make URL absolute
                        full_url = urljoin(base_url, href)
                        
                        # Check relevance
                        if (destination_lower in title.lower() or 
                            any(word in title.lower() for word in destination_lower.split())):
                            links.append(full_url)
                            if len(links) >= 15:  # Prevent too many links
                                break
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        return links
    
    async def _scrape_article(self, url: str, destination: str, interests: List[str]) -> Optional[Dict[str, Any]]:
        """Scrape content from a single article"""
        try:
            response = await self.client.get(url)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article content
            article_data = {
                "url": url,
                "activities": [],
                "restaurants": [],
                "accommodations": [],
                "local_tips": [],
                "budget_info": {},
                "safety_info": {}
            }
            
            # Get main content area
            content_selectors = [
                '.post-content', '.entry-content', '.article-content',
                '.content', 'article', '.post-body'
            ]
            
            content_div = None
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    break
            
            if not content_div:
                # Fallback to body content
                content_div = soup.find('body')
            
            if content_div:
                # Extract structured information
                text_content = content_div.text
                
                # Extract activities using pattern matching
                article_data["activities"] = self._extract_activities(text_content, interests)
                article_data["restaurants"] = self._extract_restaurants(text_content)
                article_data["accommodations"] = self._extract_accommodations(text_content)
                article_data["local_tips"] = self._extract_tips(text_content)
                article_data["budget_info"] = self._extract_budget_info(text_content)
                article_data["safety_info"] = self._extract_safety_info(text_content)
            
            return article_data
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None
    
    def _extract_activities(self, text: str, interests: List[str]) -> List[Dict[str, Any]]:
        """Extract activities from article text"""
        activities = []
        
        # Interest-based keywords
        interest_keywords = {
            "outdoor": ["hiking", "trail", "nature", "park", "beach", "mountain", "adventure", "kayak", "surf"],
            "museums": ["museum", "gallery", "art", "exhibit", "collection", "cultural", "history"],
            "theme parks": ["theme park", "amusement", "rides", "roller coaster", "disney", "universal"],
            "scenic drives": ["scenic drive", "road trip", "highway", "coastal drive", "mountain road"],
            "beaches": ["beach", "shore", "coast", "sand", "swimming", "snorkel", "dive"],
            "historic landmarks": ["historic", "monument", "landmark", "castle", "cathedral", "ancient"],
            "family friendly": ["family", "kids", "children", "playground", "zoo", "aquarium"],
            "dining hot spots": ["restaurant", "food", "dining", "cuisine", "local food", "street food"],
            "solo female": ["safe", "safety", "solo travel", "women", "female", "security"]
        }
        
        # Extract sentences that mention activities
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence is relevant to user interests
            relevant = False
            for interest in interests:
                if interest.lower() in interest_keywords:
                    keywords = interest_keywords[interest.lower()]
                    if any(keyword in sentence_lower for keyword in keywords):
                        relevant = True
                        break
            
            if relevant and len(sentence.strip()) > 20:
                # Extract activity name and description
                activity_match = re.search(r'(visit|go to|check out|explore|try|experience)\s+([^,.]{10,50})', sentence_lower)
                if activity_match:
                    activity_name = activity_match.group(2).strip()
                    activities.append({
                        "name": activity_name.title(),
                        "description": sentence.strip()[:200],
                        "category": self._categorize_activity(sentence_lower, interests),
                        "duration": self._extract_duration(sentence),
                        "cost_estimate": self._extract_cost(sentence)
                    })
        
        # Limit results and remove duplicates
        unique_activities = []
        seen_names = set()
        for activity in activities[:20]:  # Limit to 20 activities
            if activity["name"] not in seen_names:
                unique_activities.append(activity)
                seen_names.add(activity["name"])
        
        return unique_activities
    
    def _extract_restaurants(self, text: str) -> List[Dict[str, Any]]:
        """Extract restaurant information from text"""
        restaurants = []
        
        # Look for restaurant mentions
        restaurant_patterns = [
            r'(restaurant|cafe|eatery|bistro|diner)\s+([^,.]{5,30})',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(restaurant|cafe|bar)',
            r'eat at\s+([^,.]{5,30})',
            r'try\s+([^,.]{5,30})\s+for\s+(food|dining|lunch|dinner)'
        ]
        
        for pattern in restaurant_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                restaurant_name = match.group(1) if 'eat at' in pattern or 'try' in pattern else match.group(2)
                if restaurant_name and len(restaurant_name.strip()) > 3:
                    restaurants.append({
                        "name": restaurant_name.strip().title(),
                        "description": self._get_context_sentence(text, match.start()),
                        "cuisine_type": self._extract_cuisine_type(text, match.start()),
                        "price_range": self._extract_price_range(text, match.start())
                    })
        
        return restaurants[:10]  # Limit results
    
    def _extract_accommodations(self, text: str) -> List[Dict[str, Any]]:
        """Extract accommodation information from text"""
        accommodations = []
        
        accommodation_patterns = [
            r'(hotel|resort|hostel|b&b|airbnb|accommodation)\s+([^,.]{5,30})',
            r'stay at\s+([^,.]{5,30})',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(hotel|resort)'
        ]
        
        for pattern in accommodation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if 'stay at' in pattern:
                    accommodation_name = match.group(1)
                else:
                    accommodation_name = match.group(2) if match.group(2) else match.group(1)
                
                if accommodation_name and len(accommodation_name.strip()) > 3:
                    accommodations.append({
                        "name": accommodation_name.strip().title(),
                        "description": self._get_context_sentence(text, match.start()),
                        "type": self._extract_accommodation_type(text, match.start()),
                        "price_range": self._extract_price_range(text, match.start())
                    })
        
        return accommodations[:8]  # Limit results
    
    def _extract_tips(self, text: str) -> List[str]:
        """Extract local tips and advice from text"""
        tips = []
        
        # Look for tip indicators
        tip_patterns = [
            r'tip:?\s*([^.!?]{20,150})',
            r'advice:?\s*([^.!?]{20,150})',
            r'pro tip:?\s*([^.!?]{20,150})',
            r'important:?\s*([^.!?]{20,150})',
            r'note:?\s*([^.!?]{20,150})',
            r'remember:?\s*([^.!?]{20,150})'
        ]
        
        for pattern in tip_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                tip = match.group(1).strip()
                if tip and len(tip) > 15:
                    tips.append(tip)
        
        return tips[:8]  # Limit results
    
    def _extract_budget_info(self, text: str) -> Dict[str, Any]:
        """Extract budget-related information"""
        budget_info = {}
        
        # Look for cost mentions
        cost_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+)\s*dollars?',
            r'costs?\s+around\s+\$?(\d+)',
            r'budget\s+around\s+\$?(\d+)'
        ]
        
        costs = []
        for pattern in cost_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    cost = float(match.group(1).replace(',', ''))
                    costs.append(cost)
                except ValueError:
                    continue
        
        if costs:
            budget_info = {
                "estimated_daily_cost": f"${min(costs)}-${max(costs)}",
                "average_cost": f"${sum(costs)/len(costs):.0f}",
                "cost_notes": "Costs extracted from travel blog content"
            }
        
        return budget_info
    
    def _extract_safety_info(self, text: str) -> Dict[str, Any]:
        """Extract safety-related information"""
        safety_info = {}
        
        # Safety keywords and phrases
        safety_patterns = [
            r'(safe|safety|secure|dangerous|avoid|caution|warning)[^.!?]{10,100}',
            r'(crime|theft|scam|tourist trap)[^.!?]{10,100}',
            r'(solo female|women traveling|female travel)[^.!?]{10,100}'
        ]
        
        safety_notes = []
        for pattern in safety_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                safety_notes.append(match.group(0).strip())
        
        if safety_notes:
            safety_info = {
                "safety_rating": self._assess_safety_rating(text),
                "safety_notes": safety_notes[:5],  # Limit to 5 notes
                "solo_female_friendly": "solo female" in text.lower() or "women" in text.lower()
            }
        
        return safety_info
    
    def _categorize_activity(self, text: str, interests: List[str]) -> str:
        """Categorize activity based on text content and user interests"""
        for interest in interests:
            if interest.lower() in text:
                return interest
        
        # Default categorization based on keywords
        if any(word in text for word in ["museum", "gallery", "art"]):
            return "museums"
        elif any(word in text for word in ["hike", "trail", "nature"]):
            return "outdoor"
        elif any(word in text for word in ["beach", "coast", "swim"]):
            return "beaches"
        elif any(word in text for word in ["restaurant", "food", "eat"]):
            return "dining hot spots"
        else:
            return "general"
    
    def _extract_duration(self, text: str) -> Optional[str]:
        """Extract duration information from text"""
        duration_patterns = [
            r'(\d+)\s*hours?',
            r'(\d+)\s*days?',
            r'half\s+day',
            r'full\s+day'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_cost(self, text: str) -> Optional[str]:
        """Extract cost information from text"""
        cost_patterns = [
            r'\$(\d+(?:\.\d{2})?)',
            r'(\d+)\s*dollars?',
            r'free',
            r'no cost'
        ]
        
        for pattern in cost_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _get_context_sentence(self, text: str, position: int) -> str:
        """Get the sentence containing the given position"""
        # Find sentence boundaries around the position
        start = max(0, position - 100)
        end = min(len(text), position + 100)
        context = text[start:end]
        
        # Clean up and return
        return re.sub(r'\s+', ' ', context).strip()
    
    def _extract_cuisine_type(self, text: str, position: int) -> Optional[str]:
        """Extract cuisine type from context"""
        context = self._get_context_sentence(text, position)
        cuisines = ["italian", "mexican", "chinese", "japanese", "thai", "french", "indian", "greek", "american", "local"]
        
        for cuisine in cuisines:
            if cuisine in context.lower():
                return cuisine.title()
        
        return None
    
    def _extract_accommodation_type(self, text: str, position: int) -> str:
        """Extract accommodation type from context"""
        context = self._get_context_sentence(text, position).lower()
        
        if "hotel" in context:
            return "hotel"
        elif "resort" in context:
            return "resort"
        elif "hostel" in context:
            return "hostel"
        elif "b&b" in context or "bed and breakfast" in context:
            return "bed_and_breakfast"
        elif "airbnb" in context:
            return "vacation_rental"
        else:
            return "accommodation"
    
    def _extract_price_range(self, text: str, position: int) -> Optional[str]:
        """Extract price range from context"""
        context = self._get_context_sentence(text, position).lower()
        
        if any(word in context for word in ["cheap", "budget", "affordable"]):
            return "budget"
        elif any(word in context for word in ["expensive", "luxury", "high-end"]):
            return "luxury"
        elif any(word in context for word in ["moderate", "mid-range"]):
            return "mid-range"
        
        return None
    
    def _assess_safety_rating(self, text: str) -> int:
        """Assess safety rating based on text content"""
        text_lower = text.lower()
        
        # Positive safety indicators
        positive_indicators = ["safe", "secure", "peaceful", "friendly", "welcoming"]
        # Negative safety indicators  
        negative_indicators = ["dangerous", "unsafe", "crime", "theft", "avoid", "caution"]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in text_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in text_lower)
        
        # Base rating of 3, adjust based on indicators
        rating = 3
        rating += positive_count
        rating -= negative_count * 2  # Weight negative indicators more heavily
        
        return max(1, min(5, rating))  # Clamp between 1 and 5
    
    def _merge_blog_data(self, main_data: Dict[str, Any], blog_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Merge data from a single blog into the main dataset"""
        # Merge activities
        for activity in blog_data.get("activities", []):
            activity["source"] = source
            main_data["activities"].append(activity)
        
        # Merge restaurants
        for restaurant in blog_data.get("restaurants", []):
            restaurant["source"] = source
            main_data["restaurants"].append(restaurant)
        
        # Merge accommodations
        for accommodation in blog_data.get("accommodations", []):
            accommodation["source"] = source
            main_data["accommodations"].append(accommodation)
        
        # Merge tips
        main_data["local_tips"].extend(blog_data.get("local_tips", []))
        
        # Merge budget info
        if blog_data.get("budget_info"):
            if not main_data["budget_info"]:
                main_data["budget_info"] = blog_data["budget_info"]
        
        # Merge safety info
        if blog_data.get("safety_info"):
            if not main_data["safety_info"]:
                main_data["safety_info"] = blog_data["safety_info"]
        
        return main_data
    
    def _merge_article_data(self, blog_data: Dict[str, Any], article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge data from a single article into blog dataset"""
        # Merge all arrays
        for key in ["activities", "restaurants", "accommodations", "local_tips"]:
            blog_data[key].extend(article_data.get(key, []))
        
        # Merge budget and safety info (if not already present)
        if article_data.get("budget_info") and not blog_data["budget_info"]:
            blog_data["budget_info"] = article_data["budget_info"]
        
        if article_data.get("safety_info") and not blog_data["safety_info"]:
            blog_data["safety_info"] = article_data["safety_info"]
        
        return blog_data
    
    def _generate_cache_key(self, destination: str, interests: List[str]) -> str:
        """Generate cache key for destination data"""
        key_data = f"{destination}_{'-'.join(sorted(interests))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached data from database"""
        try:
            collection = self.db.blog_cache
            cached_doc = await collection.find_one({"cache_key": cache_key})
            
            if cached_doc:
                # Check if cache is still valid (24 hours)
                cache_time = cached_doc.get("cached_at")
                if cache_time:
                    cache_datetime = datetime.fromisoformat(cache_time)
                    if (datetime.utcnow() - cache_datetime).total_seconds() < 86400:  # 24 hours
                        return cached_doc.get("data")
            
            return None
        except Exception as e:
            logger.error(f"Error getting cached data: {e}")
            return None
    
    async def _cache_data(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Cache scraped data in database"""
        try:
            collection = self.db.blog_cache
            cache_doc = {
                "cache_key": cache_key,
                "data": data,
                "cached_at": datetime.utcnow().isoformat()
            }
            
            # Upsert the cache document
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