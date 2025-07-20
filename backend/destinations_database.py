# Comprehensive Global Destinations Database
# Includes major cities, hidden gems, and solo female safety ratings

from typing import Dict, List, Any

# Solo Female Safety Ratings:
# 5 = Extremely Safe - Top destinations for solo female travelers
# 4 = Very Safe - Generally safe with standard precautions  
# 3 = Moderately Safe - Safe with extra awareness
# 2 = Caution Advised - Research and preparation needed
# 1 = High Risk - Not recommended for solo female travel

DESTINATIONS_DATABASE = {
    # NORTH AMERICA - UNITED STATES
    "new_york": {
        "name": "New York City, NY",
        "country": "United States",
        "region": "North America",
        "solo_female_safety": 4,
        "safety_notes": "Very safe in Manhattan and Brooklyn. Use ride-sharing at night, avoid empty subway cars.",
        "description": "The city that never sleeps - museums, Broadway, and iconic landmarks",
        "hidden_gem": False,
        "activities": {
            "museums": [
                {
                    "name": "Metropolitan Museum of Art",
                    "category": "museums",
                    "description": "One of the world's largest and most prestigious art museums",
                    "location": {"lat": 40.7794, "lng": -73.9632},
                    "address": "1000 5th Ave, New York, NY 10028",
                    "estimated_duration": "3-4 hours",
                    "best_time": "10:00 AM - 2:00 PM",
                    "solo_female_notes": "Very safe, well-staffed, good for solo exploration"
                },
                {
                    "name": "Museum of Modern Art (MoMA)",
                    "category": "museums", 
                    "description": "Premier collection of contemporary and modern art",
                    "location": {"lat": 40.7614, "lng": -73.9776},
                    "address": "11 W 53rd St, New York, NY 10019",
                    "estimated_duration": "2-3 hours",
                    "best_time": "11:00 AM - 3:00 PM",
                    "solo_female_notes": "Excellent for solo visits, frequent security presence"
                }
            ],
            "historic landmarks": [
                {
                    "name": "Statue of Liberty",
                    "category": "historic landmarks",
                    "description": "Iconic symbol of freedom and democracy",
                    "location": {"lat": 40.6892, "lng": -74.0445},
                    "address": "Liberty Island, New York, NY 10004", 
                    "estimated_duration": "4-5 hours",
                    "best_time": "Morning ferry",
                    "solo_female_notes": "Safe ferry ride and island visit, join group tours"
                }
            ],
            "family friendly": [
                {
                    "name": "Central Park",
                    "category": "family friendly",
                    "description": "Large public park with playgrounds, lakes, and activities",
                    "location": {"lat": 40.7829, "lng": -73.9654},
                    "address": "Central Park, New York, NY",
                    "estimated_duration": "3-4 hours", 
                    "best_time": "Morning to afternoon",
                    "solo_female_notes": "Very safe during day, stick to main paths, avoid after dark"
                }
            ],
            "solo female": [
                {
                    "name": "High Line Park",
                    "category": "solo female",
                    "description": "Elevated park perfect for solo walks with great city views",
                    "location": {"lat": 40.7480, "lng": -74.0048},
                    "address": "High Line, New York, NY 10011",
                    "estimated_duration": "1-2 hours",
                    "best_time": "Morning or late afternoon",
                    "solo_female_notes": "Excellent for solo female travelers - well-patrolled, lots of people"
                }
            ]
        }
    },

    # CANADA
    "toronto": {
        "name": "Toronto, Ontario",
        "country": "Canada", 
        "region": "North America",
        "solo_female_safety": 5,
        "safety_notes": "One of the safest major cities globally. Excellent public transport and helpful locals.",
        "description": "Diverse, multicultural city with CN Tower and vibrant neighborhoods",
        "hidden_gem": False,
        "activities": {
            "historic landmarks": [
                {
                    "name": "CN Tower",
                    "category": "historic landmarks",
                    "description": "Iconic telecommunications tower with observation decks",
                    "location": {"lat": 43.6426, "lng": -79.3871},
                    "address": "290 Bremner Blvd, Toronto, ON M5V 3L9",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Sunset for best views",
                    "solo_female_notes": "Extremely safe, perfect for solo travelers"
                }
            ],
            "cultural experiences": [
                {
                    "name": "Distillery District", 
                    "category": "cultural experiences",
                    "description": "Historic cobblestone streets with art galleries and cafes",
                    "location": {"lat": 43.6503, "lng": -79.3594},
                    "address": "55 Mill St, Toronto, ON M5A 3C4",
                    "estimated_duration": "2-4 hours",
                    "best_time": "Afternoon to evening",
                    "solo_female_notes": "Very safe, pedestrian-only area, great for solo exploration"
                }
            ],
            "solo female": [
                {
                    "name": "Harbourfront Centre",
                    "category": "solo female", 
                    "description": "Cultural center by the lake with events and waterfront walks",
                    "location": {"lat": 43.6385, "lng": -79.3837},
                    "address": "235 Queens Quay W, Toronto, ON M5J 2G8",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Day or evening",
                    "solo_female_notes": "Extremely safe, well-lit waterfront, regular security patrols"
                }
            ]
        }
    },

    # HIDDEN GEM - CANADA
    "peggy_cove": {
        "name": "Peggy's Cove, Nova Scotia", 
        "country": "Canada",
        "region": "North America",
        "solo_female_safety": 5,
        "safety_notes": "Extremely safe small community. Locals are very helpful to solo travelers.",
        "description": "Picturesque fishing village with iconic lighthouse and rugged coastline",
        "hidden_gem": True,
        "activities": {
            "scenic drives": [
                {
                    "name": "Peggy's Cove Lighthouse",
                    "category": "scenic drives",
                    "description": "Canada's most photographed lighthouse on granite rocks",
                    "location": {"lat": 44.4925, "lng": -63.9168},
                    "address": "178 Peggys Point Rd, Peggys Cove, NS B3Z 3S1",
                    "estimated_duration": "1-2 hours", 
                    "best_time": "Golden hour for photography",
                    "solo_female_notes": "Very safe, small community, easy parking and walking"
                }
            ],
            "solo female": [
                {
                    "name": "Coastal Walking Trail",
                    "category": "solo female",
                    "description": "Safe coastal trail with stunning ocean views",
                    "location": {"lat": 44.4930, "lng": -63.9150},
                    "address": "Peggy's Cove, NS",
                    "estimated_duration": "30-60 minutes",
                    "best_time": "Morning or afternoon", 
                    "solo_female_notes": "Very safe trail, well-marked, other walkers usually present"
                }
            ]
        }
    },

    # MEXICO
    "mexico_city": {
        "name": "Mexico City, Mexico",
        "country": "Mexico",
        "region": "North America", 
        "solo_female_safety": 3,
        "safety_notes": "Generally safe in tourist areas like Roma Norte, Condesa. Avoid displaying valuables, use Uber.",
        "description": "Vibrant capital with incredible food, museums, and historic architecture",
        "hidden_gem": False,
        "activities": {
            "museums": [
                {
                    "name": "Frida Kahlo Museum",
                    "category": "museums",
                    "description": "The Blue House where Frida Kahlo lived and worked",
                    "location": {"lat": 19.3550, "lng": -99.1624},
                    "address": "Londres 247, Del Carmen, Coyoacán, 04100 Ciudad de México, CDMX",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Morning to avoid crowds",
                    "solo_female_notes": "Safe area (Coyoacán), book tickets online, join guided tours"
                }
            ],
            "cultural experiences": [
                {
                    "name": "Roma Norte Neighborhood",
                    "category": "cultural experiences", 
                    "description": "Hip neighborhood with galleries, cafes, and boutiques",
                    "location": {"lat": 19.4160, "lng": -99.1677},
                    "address": "Roma Norte, Mexico City, CDMX",
                    "estimated_duration": "3-4 hours",
                    "best_time": "Afternoon to evening",
                    "solo_female_notes": "Very safe neighborhood for solo female travelers, walkable and well-policed"
                }
            ],
            "solo female": [
                {
                    "name": "Condesa Park Area",
                    "category": "solo female",
                    "description": "Safe, upscale area perfect for solo female travelers",
                    "location": {"lat": 19.4095, "lng": -99.1720},
                    "address": "Condesa, Mexico City, CDMX", 
                    "estimated_duration": "2-3 hours",
                    "best_time": "Day to evening",
                    "solo_female_notes": "Excellent for solo women - safe, trendy, good restaurants and cafes"
                }
            ]
        }
    },

    # EUROPE - MAJOR CITIES
    "london": {
        "name": "London, UK",
        "country": "United Kingdom",
        "region": "Europe",
        "solo_female_safety": 4,
        "safety_notes": "Generally very safe. Be aware of pickpockets in tourist areas. Public transport excellent.",
        "description": "Historic capital with world-class museums, royal palaces, and diverse culture",
        "hidden_gem": False,
        "activities": {
            "museums": [
                {
                    "name": "British Museum",
                    "category": "museums",
                    "description": "World's largest collection of historical artifacts and art",
                    "location": {"lat": 51.5194, "lng": -0.1270},
                    "address": "Great Russell St, London WC1B 3DG, UK",
                    "estimated_duration": "4-6 hours",
                    "best_time": "Early morning to avoid crowds",
                    "solo_female_notes": "Very safe, excellent for solo exploration"
                },
                {
                    "name": "Tate Modern",
                    "category": "museums",
                    "description": "Premier modern and contemporary art gallery",
                    "location": {"lat": 51.5076, "lng": -0.0994},
                    "address": "Bankside, London SE1 9TG, UK",
                    "estimated_duration": "3-4 hours",
                    "best_time": "Afternoon",
                    "solo_female_notes": "Safe, well-staffed, great for solo art lovers"
                }
            ],
            "historic landmarks": [
                {
                    "name": "Tower of London",
                    "category": "historic landmarks",
                    "description": "Historic castle and home to the Crown Jewels",
                    "location": {"lat": 51.5081, "lng": -0.0759},
                    "address": "St Katharine's & Wapping, London EC3N 4AB, UK",
                    "estimated_duration": "3-4 hours",
                    "best_time": "Early morning",
                    "solo_female_notes": "Very safe, guided tours available"
                },
                {
                    "name": "Westminster Abbey",
                    "category": "historic landmarks",
                    "description": "Gothic abbey church where monarchs are crowned",
                    "location": {"lat": 51.4994, "lng": -0.1273},
                    "address": "20 Deans Yd, Westminster, London SW1P 3PA, UK",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Morning",
                    "solo_female_notes": "Safe, audio guides available for solo visitors"
                }
            ],
            "solo female": [
                {
                    "name": "Covent Garden",
                    "category": "solo female",
                    "description": "Vibrant market area perfect for solo exploration",
                    "location": {"lat": 51.5118, "lng": -0.1226},
                    "address": "Covent Garden, London WC2E, UK",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Afternoon",
                    "solo_female_notes": "Excellent for solo female travelers - safe, lively, great shopping and cafes"
                }
            ]
        }
    },

    "paris": {
        "name": "Paris, France",
        "country": "France",
        "region": "Europe",
        "solo_female_safety": 4,
        "safety_notes": "Generally very safe. Be aware of pickpockets in tourist areas. Metro safe during day.",
        "description": "City of Light with world-class museums, cuisine, and romantic atmosphere",
        "hidden_gem": False,
        "activities": {
            "museums": [
                {
                    "name": "Louvre Museum",
                    "category": "museums",
                    "description": "World's largest art museum housing the Mona Lisa",
                    "location": {"lat": 48.8606, "lng": 2.3376}, 
                    "address": "Rue de Rivoli, 75001 Paris, France",
                    "estimated_duration": "4-6 hours",
                    "best_time": "Early morning or late afternoon",
                    "solo_female_notes": "Very safe, excellent for solo visits, book timed entry"
                }
            ],
            "historic landmarks": [
                {
                    "name": "Eiffel Tower",
                    "category": "historic landmarks",
                    "description": "Iconic iron lattice tower and symbol of Paris",
                    "location": {"lat": 48.8584, "lng": 2.2945},
                    "address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Sunset for best photos",
                    "solo_female_notes": "Very safe area, well-patrolled, great for solo photos"
                }
            ],
            "solo female": [
                {
                    "name": "Marais District",
                    "category": "solo female",
                    "description": "Historic district perfect for solo exploration with cafes and boutiques",
                    "location": {"lat": 48.8566, "lng": 2.3522},
                    "address": "Le Marais, Paris, France",
                    "estimated_duration": "3-4 hours",
                    "best_time": "Afternoon",
                    "solo_female_notes": "Excellent for solo female travelers - safe, walkable, lots to see"
                }
            ]
        }
    },

    # HIDDEN GEM - EUROPE 
    "cesky_krumlov": {
        "name": "Český Krumlov, Czech Republic",
        "country": "Czech Republic",
        "region": "Europe",
        "solo_female_safety": 5,
        "safety_notes": "Extremely safe small town. One of the safest places in Europe for solo female travel.",
        "description": "Fairytale medieval town with castle and winding cobblestone streets", 
        "hidden_gem": True,
        "activities": {
            "historic landmarks": [
                {
                    "name": "Český Krumlov Castle",
                    "category": "historic landmarks",
                    "description": "13th-century castle complex overlooking the Vltava River",
                    "location": {"lat": 48.8127, "lng": 14.3175},
                    "address": "Zámek 59, 381 01 Český Krumlov, Czechia",
                    "estimated_duration": "3-4 hours",
                    "best_time": "Morning for fewer crowds",
                    "solo_female_notes": "Extremely safe, perfect for solo exploration, English tours available"
                }
            ],
            "scenic drives": [
                {
                    "name": "Old Town Walking Tour",
                    "category": "scenic drives", 
                    "description": "Medieval streets perfect for leisurely strolling",
                    "location": {"lat": 48.8101, "lng": 14.3153},
                    "address": "Historic Center, Český Krumlov, Czechia",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Anytime",
                    "solo_female_notes": "Extremely safe for solo walking, very friendly locals"
                }
            ],
            "solo female": [
                {
                    "name": "Vltava River Views",
                    "category": "solo female",
                    "description": "Peaceful riverside walks perfect for solo reflection",
                    "location": {"lat": 48.8105, "lng": 14.3140},
                    "address": "Český Krumlov, Czechia",
                    "estimated_duration": "1-2 hours", 
                    "best_time": "Early morning or late afternoon",
                    "solo_female_notes": "Extremely peaceful and safe, perfect for solo female travelers"
                }
            ]
        }
    },

    # ASIA - MAJOR CITIES
    "tokyo": {
        "name": "Tokyo, Japan", 
        "country": "Japan",
        "region": "Asia",
        "solo_female_safety": 5,
        "safety_notes": "One of the safest major cities globally. Extremely low crime rate, helpful police.",
        "description": "Blend of ultra-modern and traditional culture, incredible food scene",
        "hidden_gem": False,
        "activities": {
            "cultural experiences": [
                {
                    "name": "Senso-ji Temple",
                    "category": "cultural experiences",
                    "description": "Tokyo's oldest temple in historic Asakusa district",
                    "location": {"lat": 35.7148, "lng": 139.7967},
                    "address": "2-3-1 Asakusa, Taito City, Tokyo 111-0032, Japan",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Early morning for fewer crowds",
                    "solo_female_notes": "Extremely safe, perfect for solo cultural exploration"
                }
            ],
            "family friendly": [
                {
                    "name": "Ueno Park",
                    "category": "family friendly",
                    "description": "Large park with museums, zoo, and cherry blossoms",
                    "location": {"lat": 35.7144, "lng": 139.7744},
                    "address": "Uenokoen, Taito City, Tokyo 110-0007, Japan", 
                    "estimated_duration": "3-4 hours",
                    "best_time": "Morning to afternoon",
                    "solo_female_notes": "Extremely safe, great for solo park walks and museum visits"
                }
            ],
            "solo female": [
                {
                    "name": "Shibuya Crossing",
                    "category": "solo female",
                    "description": "World's busiest pedestrian crossing, iconic Tokyo experience", 
                    "location": {"lat": 35.6598, "lng": 139.7006},
                    "address": "Shibuya City, Tokyo, Japan",
                    "estimated_duration": "1-2 hours",
                    "best_time": "Evening for the full experience",
                    "solo_female_notes": "Extremely safe even with crowds, perfect solo experience"
                }
            ]
        }
    },

    # HIDDEN GEM - ASIA
    "luang_prabang": {
        "name": "Luang Prabang, Laos",
        "country": "Laos", 
        "region": "Asia",
        "solo_female_safety": 4,
        "safety_notes": "Generally safe for solo female travelers. Conservative dress recommended. Avoid walking alone very late.",
        "description": "UNESCO World Heritage town with Buddhist temples and French colonial architecture",
        "hidden_gem": True,
        "activities": {
            "cultural experiences": [
                {
                    "name": "Alms Ceremony",
                    "category": "cultural experiences", 
                    "description": "Traditional Buddhist morning alms giving ceremony",
                    "location": {"lat": 19.8845, "lng": 102.1348},
                    "address": "Sisavangvong Road, Luang Prabang, Laos",
                    "estimated_duration": "1 hour",
                    "best_time": "6:00 AM",
                    "solo_female_notes": "Safe cultural experience, maintain respectful distance, dress modestly"
                }
            ],
            "scenic drives": [
                {
                    "name": "Kuang Si Falls",
                    "category": "scenic drives",
                    "description": "Multi-tiered waterfall with turquoise pools",
                    "location": {"lat": 19.7489, "lng": 102.0714},
                    "address": "Kuang Si Falls, Luang Prabang, Laos",
                    "estimated_duration": "4-5 hours including travel",
                    "best_time": "Morning for best lighting",
                    "solo_female_notes": "Safe with tour groups, swimming allowed in designated areas"
                }
            ],
            "solo female": [
                {
                    "name": "Night Market",
                    "category": "solo female",
                    "description": "Evening handicraft market perfect for solo browsing",
                    "location": {"lat": 19.8854, "lng": 102.1351},
                    "address": "Sisavangvong Road, Luang Prabang, Laos",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Evening after 6 PM", 
                    "solo_female_notes": "Safe for solo female shopping, well-lit, friendly vendors"
                }
            ]
        }
    },

    # SOUTH AMERICA
    "buenos_aires": {
        "name": "Buenos Aires, Argentina",
        "country": "Argentina",
        "region": "South America", 
        "solo_female_safety": 3,
        "safety_notes": "Generally safe in tourist areas like Palermo, Recoleta. Use official taxis, avoid showing valuables.",
        "description": "Paris of South America with tango, steak, and European architecture",
        "hidden_gem": False,
        "activities": {
            "cultural experiences": [
                {
                    "name": "San Telmo Sunday Market",
                    "category": "cultural experiences",
                    "description": "Historic neighborhood market with tango performances",
                    "location": {"lat": -34.6211, "lng": -58.3731},
                    "address": "Defensa 1179, C1065 CABA, Argentina",
                    "estimated_duration": "3-4 hours",
                    "best_time": "Sunday afternoon",
                    "solo_female_notes": "Safe during market hours, stay in main tourist areas"
                }
            ],
            "historic landmarks": [
                {
                    "name": "Recoleta Cemetery", 
                    "category": "historic landmarks",
                    "description": "Famous cemetery where Eva Perón is buried",
                    "location": {"lat": -34.5877, "lng": -58.3923},
                    "address": "Junín 1760, C1113 CABA, Argentina",
                    "estimated_duration": "1-2 hours",
                    "best_time": "Morning or afternoon",
                    "solo_female_notes": "Very safe area (Recoleta), well-maintained, security present"
                }
            ],
            "solo female": [
                {
                    "name": "Palermo Neighborhood",
                    "category": "solo female",
                    "description": "Trendy neighborhood perfect for solo exploration",
                    "location": {"lat": -34.5875, "lng": -58.4270},
                    "address": "Palermo, Buenos Aires, Argentina",
                    "estimated_duration": "4-6 hours",
                    "best_time": "Afternoon to evening",
                    "solo_female_notes": "Very safe for solo female travelers, upscale area with good restaurants"
                }
            ]
        }
    },

    # AUSTRALIA
    "melbourne": {
        "name": "Melbourne, Australia",
        "country": "Australia",
        "region": "Australia/Oceania",
        "solo_female_safety": 5,
        "safety_notes": "Extremely safe city. Excellent public transport. Very solo-female-friendly culture.",
        "description": "Cultural capital with coffee culture, street art, and diverse food scene",
        "hidden_gem": False,
        "activities": {
            "cultural experiences": [
                {
                    "name": "Hosier Lane Street Art",
                    "category": "cultural experiences",
                    "description": "Famous laneway covered in ever-changing street art",
                    "location": {"lat": -37.8162, "lng": 144.9692},
                    "address": "Hosier Ln, Melbourne VIC 3000, Australia",
                    "estimated_duration": "1-2 hours", 
                    "best_time": "Anytime",
                    "solo_female_notes": "Very safe, central location, perfect for solo photography"
                }
            ],
            "family friendly": [
                {
                    "name": "Royal Botanic Gardens",
                    "category": "family friendly",
                    "description": "Beautiful gardens along the Yarra River",
                    "location": {"lat": -37.8304, "lng": 144.9796},
                    "address": "Birdwood Ave, Melbourne VIC 3004, Australia",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Morning to afternoon",
                    "solo_female_notes": "Extremely safe, perfect for solo walks and picnics"
                }
            ],
            "solo female": [
                {
                    "name": "Federation Square",
                    "category": "solo female",
                    "description": "Cultural hub perfect for solo travelers to people-watch",
                    "location": {"lat": -37.8179, "lng": 144.9690},
                    "address": "Flinders St & Swanston St, Melbourne VIC 3000, Australia",
                    "estimated_duration": "2-3 hours",
                    "best_time": "Afternoon to evening",
                    "solo_female_notes": "Extremely safe, central meeting point, lots of activities"
                }
            ]
        }
    }
}

# Additional European Hidden Gems
EUROPEAN_HIDDEN_GEMS = {
    "sintra": {
        "name": "Sintra, Portugal",
        "country": "Portugal", 
        "region": "Europe",
        "solo_female_safety": 5,
        "safety_notes": "Extremely safe small town. Perfect for solo female travelers.",
        "description": "Fairytale town with colorful palaces and romantic gardens",
        "hidden_gem": True
    },
    "hallstatt": {
        "name": "Hallstatt, Austria", 
        "country": "Austria",
        "region": "Europe", 
        "solo_female_safety": 5,
        "safety_notes": "One of the safest places in Europe. Tiny village, very welcoming.",
        "description": "Picture-perfect lakeside village in the Austrian Alps",
        "hidden_gem": True
    },
    "rothenburg": {
        "name": "Rothenburg ob der Tauber, Germany",
        "country": "Germany",
        "region": "Europe",
        "solo_female_safety": 5, 
        "safety_notes": "Extremely safe medieval town. Perfect for solo exploration.",
        "description": "Best-preserved medieval town in Germany",
        "hidden_gem": True
    }
}

# Safety Guidelines for Solo Female Travelers
SOLO_FEMALE_SAFETY_GUIDELINES = {
    "general_tips": [
        "Research accommodation in safe, well-reviewed areas",
        "Share your itinerary with someone at home", 
        "Trust your instincts - if something feels wrong, leave",
        "Dress appropriately for local culture and customs",
        "Keep emergency contacts and embassy information handy",
        "Use official transportation options when possible",
        "Stay confident and aware of your surroundings"
    ],
    "accommodation_tips": [
        "Choose well-reviewed accommodations in safe neighborhoods",
        "Consider female-only hostels or guesthouses",
        "Book accommodations near public transportation",
        "Read recent reviews from other solo female travelers"
    ],
    "transportation_tips": [
        "Use official ride-sharing apps or registered taxis",
        "Sit near the driver on public transport if possible", 
        "Avoid walking alone late at night in unfamiliar areas",
        "Keep transportation apps downloaded and ready to use"
    ]
}

def get_destinations_by_region(region: str = None) -> Dict[str, Any]:
    """Get destinations filtered by region"""
    if not region:
        return DESTINATIONS_DATABASE
    
    return {k: v for k, v in DESTINATIONS_DATABASE.items() if v["region"].lower() == region.lower()}

def get_solo_female_safe_destinations(min_safety_rating: int = 4) -> Dict[str, Any]:
    """Get destinations with high solo female safety ratings"""
    return {k: v for k, v in DESTINATIONS_DATABASE.items() if v["solo_female_safety"] >= min_safety_rating}

def get_hidden_gems() -> Dict[str, Any]:
    """Get lesser-known destinations"""
    return {k: v for k, v in DESTINATIONS_DATABASE.items() if v.get("hidden_gem", False)}

def search_destinations_by_interest(interest: str) -> Dict[str, Any]:
    """Find destinations that offer specific interests"""
    matching_destinations = {}
    
    for dest_key, dest_data in DESTINATIONS_DATABASE.items():
        if "activities" in dest_data and interest.lower() in dest_data["activities"]:
            matching_destinations[dest_key] = dest_data
            
    return matching_destinations