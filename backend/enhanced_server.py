"""
Optimized FastAPI server for Render deployment
Faster startup with minimal dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import json
from typing import List, Dict, Any
import asyncio
import httpx

# Create FastAPI app
app = FastAPI(
    title="Dream Travels API",
    description="Optimized travel planning API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Comprehensive destinations database with 50+ global destinations
DESTINATIONS = {
    # Europe
    "paris": {
        "name": "Paris, France",
        "description": "The City of Light captivates with its romantic boulevards, world-renowned museums, and timeless elegance. From the iconic Eiffel Tower to charming Montmartre cafés, Paris offers an unmatched blend of art, culture, and culinary excellence.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe",
        "region": "Western Europe",
        "country": "France",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHxsYW5kbWFya3xlbnwwfHx8fDE3NTQ0NDI0OTh8MA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Eiffel Tower"
    },
    "london": {
        "name": "London, UK", 
        "description": "A magnificent blend of royal heritage and modern innovation, London offers world-class museums, historic palaces, and vibrant neighborhoods. From Big Ben to trendy Borough Market, the city seamlessly weaves together centuries of history with contemporary culture.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe",
        "region": "Western Europe",
        "country": "United Kingdom",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxfHxhcmNoaXRlY3R1cmV8ZW58MHx8fHwxNzU0NDQyNTA1fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Big Ben & Houses of Parliament"
    },
    "rome": {
        "name": "Rome, Italy",
        "description": "The Eternal City where ancient history meets vibrant modern life. Walk through 2,000 years of civilization as you explore the Colosseum, Vatican treasures, and indulge in authentic Roman cuisine in charming piazzas.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "Europe",
        "region": "Southern Europe",
        "country": "Italy",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwzfHxhcmNoaXRlY3R1cmV8ZW58MHx8fHwxNzU0NDQyNTA1fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Colosseum"
    },
    "barcelona": {
        "name": "Barcelona, Spain", 
        "description": "A Mediterranean masterpiece where Gaudí's whimsical architecture meets golden beaches. Barcelona enchants with its artistic soul, from the breathtaking Sagrada Familia to the lively Las Ramblas and vibrant tapas culture.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "Europe",
        "region": "Southern Europe",
        "country": "Spain",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1539037116277-4db20889f2d4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHw0fHxhcmNoaXRlY3R1cmV8ZW58MHx8fHwxNzU0NDQyNTA1fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Sagrada Familia"
    },
    "amsterdam": {
        "name": "Amsterdam, Netherlands",
        "description": "A charming canal city that effortlessly blends rich history with progressive culture. Cycle along tree-lined canals, explore world-class museums, and experience the welcoming Dutch hospitality in this picturesque European gem.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe",
        "region": "Western Europe",
        "country": "Netherlands",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1534351590666-13e3e96b5017?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHw1fHxhcmNoaXRlY3R1cmV8ZW58MHx8fHwxNzU0NDQyNTA1fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Canal Houses"
    },
    "berlin": {
        "name": "Berlin, Germany",
        "description": "A dynamic capital that has risen from its complex past to become a hub of creativity and innovation. Berlin captivates with its historic landmarks, vibrant street art scene, and an electrifying nightlife unlike anywhere else in Europe.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe",
        "region": "Central Europe",
        "country": "Germany",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1560969184-10fe8719e047?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHw2fHxhcmNoaXRlY3R1cmV8ZW58MHx8fHwxNzU0NDQyNTA1fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Brandenburg Gate"
    },
    "vienna": {
        "name": "Vienna, Austria",
        "description": "An imperial city where classical music echoes through grand palaces and elegant coffeehouses. Vienna enchants visitors with its architectural splendor, rich cultural heritage, and reputation as one of the world's most livable cities.",
        "safety_rating": 5,
        "solo_female_rating": 5,
        "continent": "Europe",
        "region": "Central Europe",
        "country": "Austria",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1485465053475-dd55ed3894b9?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzh8MHwxfHNlYXJjaHwzfHxjYXN0bGV8ZW58MHx8fHwxNzU0NDQyNTI4fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Schönbrunn Palace"
    },
    "prague": {
        "name": "Prague, Czech Republic",
        "description": "A fairy-tale city of a hundred spires, where medieval charm meets bohemian spirit. Prague's stunning Gothic and Baroque architecture, historic castle, and legendary beer culture make it one of Europe's most enchanting destinations.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe",
        "region": "Central Europe",
        "country": "Czech Republic",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1596414086775-3e321ab08f36?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHw3fHxhcmNoaXRlY3R1cmV8ZW58MHx8fHwxNzU0NDQyNTA1fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Charles Bridge"
    },
    "budapest": {
        "name": "Budapest, Hungary",
        "description": "The Pearl of the Danube, where thermal baths meet grand architecture. Budapest captivates with its dramatic parliament building, historic castles, and unique ruin bars, offering an authentic Central European experience.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe",
        "region": "Central Europe",
        "country": "Hungary",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1541849546-216549ae216d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHw4fHxhcmNoaXRlY3R1cmV8ZW58MHx8fHwxNzU0NDQyNTA1fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Hungarian Parliament Building"
    },
    "copenhagen": {
        "name": "Copenhagen, Denmark",
        "description": "A Scandinavian gem where hygge culture meets innovative design. Copenhagen charms with its colorful Nyhavn harbor, world-class dining scene, and commitment to sustainability, making it a perfect blend of coziness and modernity.",
        "safety_rating": 5,
        "solo_female_rating": 5,
        "continent": "Europe",
        "region": "Northern Europe",
        "country": "Denmark",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1527576539890-dfa815648363?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwyfHxhcmNoaXRlY3R1cmV8ZW58MHx8fHwxNzU0NDQyNTA1fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Nyhavn Colorful Houses"
    },
    "stockholm": {
        "name": "Stockholm, Sweden",
        "description": "The Venice of the North, spread across 14 islands connected by graceful bridges. Stockholm combines medieval charm in Gamla Stan with cutting-edge Scandinavian design, creating a city that's both historic and refreshingly modern.",
        "safety_rating": 5,
        "solo_female_rating": 5,
        "continent": "Europe",
        "region": "Northern Europe",
        "country": "Sweden",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1509356843151-3e7d96241e11?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHw5fHxhcmNoaXRlY3R1cmV8ZW58MHx8fHwxNzU0NDQyNTA1fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Gamla Stan Old Town"
    },
    "reykjavik": {
        "name": "Reykjavik, Iceland",
        "description": "The world's northernmost capital, serving as gateway to Iceland's otherworldly landscapes. Reykjavik captivates with its vibrant cultural scene, colorful houses, and proximity to natural wonders like Northern Lights and geothermal springs.",
        "safety_rating": 5,
        "solo_female_rating": 5,
        "continent": "Europe",
        "region": "Northern Europe",
        "country": "Iceland",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxMHx8YXJjaGl0ZWN0dXJlfGVufDB8fHx8MTc1NDQ0MjUwNXww&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Hallgrimskirkja Church"
    },
    "dubrovnik": {
        "name": "Dubrovnik, Croatia",
        "description": "The Pearl of the Adriatic, where medieval walls embrace crystal-clear waters. Dubrovnik enchants with its perfectly preserved Old Town, dramatic coastal setting, and rich maritime history that earned it UNESCO World Heritage status.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe",
        "region": "Southern Europe",
        "country": "Croatia",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1605540436563-5bca919ae766?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxMXx8YXJjaGl0ZWN0dXJlfGVufDB8fHx8MTc1NDQ0MjUwNXww&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "City Walls & Old Town"
    },
    "porto": {
        "name": "Porto, Portugal",
        "description": "A riverside jewel famous for port wine and stunning azulejo tiles. Porto captivates with its dramatic bridges over the Douro River, historic wine cellars, and a beautifully preserved city center that tells centuries of Portuguese history.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe",
        "region": "Southern Europe",
        "country": "Portugal",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1555881400-74d7acaacd8b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxMnx8YXJjaGl0ZWN0dXJlfGVufDB8fHx8MTc1NDQ0MjUwNXww&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Dom Luis I Bridge"
    },
    "edinburgh": {
        "name": "Edinburgh, Scotland",
        "description": "Scotland's historic capital, where a dramatic castle overlooks a city of festivals and culture. Edinburgh combines ancient traditions with vibrant creativity, from the famous Royal Mile to the world's largest arts festival every August.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Europe",
        "region": "Western Europe",
        "country": "United Kingdom",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1565362243149-6bf6bcba7db2?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzF8MHwxfHNlYXJjaHwxM3x8YXJjaGl0ZWN0dXJlfGVufDB8fHx8MTc1NDQ0MjUwNXww&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Edinburgh Castle"
    },

    # North America
    "new_york": {
        "name": "New York, NY",
        "description": "The city that never sleeps, where towering skyscrapers meet endless possibilities. From the bright lights of Times Square to the serenity of Central Park, New York offers an unmatched urban experience with world-class museums, Broadway shows, and iconic landmarks.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "North America",
        "region": "Northeast USA",
        "country": "United States",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1503572327579-b5c6afe5c5c5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw0fHxsYW5kbWFya3xlbnwwfHx8fDE3NTQ0NDI0OTh8MA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Statue of Liberty"
    },
    "san_francisco": {
        "name": "San Francisco, CA",
        "description": "A city of rolling hills and stunning bay views, where innovation meets natural beauty. San Francisco captivates with its iconic Golden Gate Bridge, historic cable cars, diverse neighborhoods, and a thriving tech and cultural scene.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "North America",
        "region": "West Coast USA",
        "country": "United States",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1429041966141-44d228a42775?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwxfHxicmlkZ2V8ZW58MHx8fHwxNzU0NDQyNTE2fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Golden Gate Bridge"
    },
    "los_angeles": {
        "name": "Los Angeles, CA",
        "description": "The entertainment capital of the world, where Hollywood dreams meet year-round sunshine. Los Angeles offers glamorous beaches, world-class museums, diverse neighborhoods, and the chance to experience the magic of the film industry.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "North America",
        "region": "West Coast USA",
        "country": "United States",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1444723121833-7a298aa2c9c8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw1fHxjaXR5c2NhcGV8ZW58MHx8fHwxNzU0NDQyNTExfDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Hollywood Sign"
    },
    "chicago": {
        "name": "Chicago, IL",
        "description": "The Windy City, renowned for its bold architecture and deep-dish pizza. Chicago impresses with its stunning skyline, world-class museums, vibrant music scene, and friendly Midwest hospitality along the shores of Lake Michigan.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "North America",
        "region": "Midwest USA",
        "country": "United States",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1477414348463-c0eb7f1359b6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw2fHxjaXR5c2NhcGV8ZW58MHx8fHwxNzU0NDQyNTExfDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Willis Tower & Skyline"
    },
    "toronto": {
        "name": "Toronto, Canada",
        "description": "Canada's multicultural metropolis, where the iconic CN Tower dominates a diverse and dynamic cityscape. Toronto offers world-class dining, thriving arts scene, and neighborhoods that celebrate cultures from around the globe.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "North America",
        "region": "Central Canada",
        "country": "Canada",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1517390047777-5bc442b97cc4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw3fHxjaXR5c2NhcGV8ZW58MHx8fHwxNzU0NDQyNTExfDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "CN Tower"
    },
    "vancouver": {
        "name": "Vancouver, Canada",
        "description": "A stunning Pacific Northwest gem nestled between mountains and ocean. Vancouver combines outdoor adventure with urban sophistication, offering spectacular natural beauty, diverse cuisine, and a laid-back West Coast lifestyle.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "North America",
        "region": "Western Canada",
        "country": "Canada",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1549057446-7d6426fa015b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw4fHxjaXR5c2NhcGV8ZW58MHx8fHwxNzU0NDQyNTExfDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Lions Gate Bridge"
    },
    "montreal": {
        "name": "Montreal, Canada",
        "description": "European charm in North America, where French culture thrives in a vibrant, creative atmosphere. Montreal enchants with its cobblestone Old Town, festival culture, incredible food scene, and unique blend of old-world romance and modern energy.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "North America",
        "region": "Eastern Canada",
        "country": "Canada",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1585584114963-503344a119b0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHw5fHxjaXR5c2NhcGV8ZW58MHx8fHwxNzU0NDQyNTExfDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Old Montreal"
    },
    "seattle": {
        "name": "Seattle, WA",
        "description": "The Emerald City, where innovation meets natural beauty in the Pacific Northwest. Seattle captivates with its thriving coffee culture, iconic Space Needle, vibrant music scene, and stunning views of mountains and Puget Sound.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "North America",
        "region": "Pacific Northwest",
        "country": "United States",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxMHx8Y2l0eXNjYXBlfGVufDB8fHx8MTc1NDQ0MjUxMXww&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Space Needle"
    },
    "mexico_city": {
        "name": "Mexico City, Mexico",
        "description": "A vibrant megacity where ancient Aztec heritage meets contemporary Mexican culture. Mexico City dazzles with incredible museums, street art, authentic cuisine, and a rich cultural tapestry that spans centuries of fascinating history.",
        "safety_rating": 2,
        "solo_female_rating": 2,
        "continent": "North America",
        "region": "Central Mexico",
        "country": "Mexico",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1585464231875-d9ef1f5ad396?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxMXx8Y2l0eXNjYXBlfGVufDB8fHx8MTc1NDQ0MjUxMXww&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Zócalo & Metropolitan Cathedral"
    },

    # Asia
    "tokyo": {
        "name": "Tokyo, Japan",
        "description": "A mesmerizing metropolis where ancient traditions seamlessly blend with cutting-edge technology. Tokyo offers everything from serene temples and traditional gardens to neon-lit districts and world-class cuisine, creating an unforgettable urban experience.",
        "safety_rating": 5,
        "solo_female_rating": 5,
        "continent": "Asia",
        "region": "East Asia",
        "country": "Japan",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1716220902614-cbe6d1d9af09?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwzfHxsYW5kbWFya3xlbnwwfHx8fDE3NTQ0NDI0OTh8MA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Tokyo Tower & Skyline"
    },
    "kyoto": {
        "name": "Kyoto, Japan",
        "description": "Japan's ancient capital, where thousands of temples and shrines preserve centuries of culture and tradition. Kyoto enchants visitors with its bamboo forests, traditional geisha districts, and some of the most beautiful gardens in the world.",
        "safety_rating": 5,
        "solo_female_rating": 5,
        "continent": "Asia",
        "region": "East Asia",
        "country": "Japan",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxMnx8Y2l0eXNjYXBlfGVufDB8fHx8MTc1NDQ0MjUxMXww&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Fushimi Inari Shrine"
    },
    "singapore": {
        "name": "Singapore",
        "description": "A gleaming city-state where East meets West in perfect harmony. Singapore captivates with its futuristic architecture, incredible street food, lush gardens, and reputation as one of the world's safest and most efficient cities.",
        "safety_rating": 5,
        "solo_female_rating": 5,
        "continent": "Asia",
        "region": "Southeast Asia",
        "country": "Singapore",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1496368077930-c1e31b4e5b44?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxM3x8Y2l0eXNjYXBlfGVufDB8fHx8MTc1NDQ0MjUxMXww&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Marina Bay Sands"
    },
    "hong_kong": {
        "name": "Hong Kong",
        "description": "A dynamic fusion of East and West, where stunning skyscrapers rise from Victoria Harbor. Hong Kong offers world-class shopping, incredible dim sum, bustling street markets, and breathtaking views from Victoria Peak.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Asia",
        "region": "East Asia",
        "country": "Hong Kong",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1536599018102-9f803c140fc1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxNHx8Y2l0eXNjYXBlfGVufDB8fHx8MTc1NDQ0MjUxMXww&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Victoria Harbor Skyline"
    },
    "seoul": {
        "name": "Seoul, South Korea",
        "description": "A high-tech capital where K-culture meets ancient palaces. Seoul offers cutting-edge technology, incredible street food, vibrant nightlife, and a perfect blend of traditional Korean culture with modern innovation.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Asia",
        "region": "East Asia",
        "country": "South Korea",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1478436127897-769e1b3f0f36?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxNXx8Y2l0eXNjYXBlfGVufDB8fHx8MTc1NDQ0MjUxMXww&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Gyeongbokgung Palace"
    },
    "bangkok": {
        "name": "Bangkok, Thailand",
        "description": "A vibrant capital where golden temples meet bustling street markets. Bangkok captivates with its incredible street food scene, ornate Buddhist temples, floating markets, and the warm hospitality of Thai culture.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "Asia",
        "region": "Southeast Asia",
        "country": "Thailand",
        "hidden_gem": False,
        "image_url": "https://images.pexels.com/photos/3077996/pexels-photo-3077996.jpeg?auto=compress&cs=tinysrgb",
        "iconic_landmark": "Wat Arun (Temple of Dawn)"
    },
    "kuala_lumpur": {
        "name": "Kuala Lumpur, Malaysia",
        "description": "A modern metropolis where towering skyscrapers meet diverse cultural heritage. Kuala Lumpur offers incredible cuisine fusion, the iconic Petronas Towers, bustling markets, and a unique blend of Malay, Chinese, and Indian cultures.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "Asia",
        "region": "Southeast Asia",
        "country": "Malaysia",
        "hidden_gem": True,
        "image_url": "https://images.pexels.com/photos/162031/dubai-tower-arab-khalifa-162031.jpeg?auto=compress&cs=tinysrgb",
        "iconic_landmark": "Petronas Twin Towers"
    },
    "bali": {
        "name": "Bali, Indonesia",
        "description": "A tropical paradise where ancient Hindu temples meet pristine beaches and emerald rice terraces. Bali offers spiritual serenity, world-class surfing, vibrant arts scene, and warm Indonesian hospitality in an island setting.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "Asia",
        "region": "Southeast Asia",
        "country": "Indonesia",
        "hidden_gem": False,
        "image_url": "https://images.pexels.com/photos/1141853/pexels-photo-1141853.jpeg?auto=compress&cs=tinysrgb",
        "iconic_landmark": "Tanah Lot Temple"
    },
    "vietnam_ho_chi_minh": {
        "name": "Ho Chi Minh City, Vietnam",
        "description": "A dynamic city where French colonial elegance meets Vietnamese street food culture. Ho Chi Minh City pulses with energy, offering historic landmarks, incredible pho and street food, and a glimpse into Vietnam's fascinating past and present.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "Asia",
        "region": "Southeast Asia",
        "country": "Vietnam",
        "hidden_gem": True,
        "image_url": "https://images.pexels.com/photos/753339/pexels-photo-753339.jpeg?auto=compress&cs=tinysrgb",
        "iconic_landmark": "Saigon Notre-Dame Basilica"
    },
    "mumbai": {
        "name": "Mumbai, India",
        "description": "The entertainment capital of India, where Bollywood glamour meets bustling street life. Mumbai offers incredible energy, historic architecture, diverse street food, and a unique blend of traditional Indian culture with modern ambition.",
        "safety_rating": 2,
        "solo_female_rating": 2,
        "continent": "Asia",
        "region": "South Asia",
        "country": "India",
        "hidden_gem": False,
        "image_url": "https://images.pexels.com/photos/262367/pexels-photo-262367.jpeg?auto=compress&cs=tinysrgb",
        "iconic_landmark": "Gateway of India"
    },
    "istanbul": {
        "name": "Istanbul, Turkey",
        "description": "A magnificent bridge between Europe and Asia, where Byzantine and Ottoman history create an enchanting atmosphere. Istanbul captivates with its stunning mosques, bustling bazaars, Bosphorus views, and rich cultural heritage.",
        "safety_rating": 3,
        "solo_female_rating": 2,
        "continent": "Asia",
        "region": "Western Asia",
        "country": "Turkey",
        "hidden_gem": False,
        "image_url": "https://images.pexels.com/photos/1109541/pexels-photo-1109541.jpeg?auto=compress&cs=tinysrgb",
        "iconic_landmark": "Hagia Sophia"
    },
    "dubai": {
        "name": "Dubai, UAE",
        "description": "A futuristic oasis where luxury meets innovation in the desert. Dubai dazzles with its record-breaking skyscrapers, world-class shopping, artificial islands, and unique blend of traditional Arabian culture with modern extravagance.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Asia",
        "region": "Middle East",
        "country": "United Arab Emirates",
        "hidden_gem": False,
        "image_url": "https://images.pexels.com/photos/162031/dubai-tower-arab-khalifa-162031.jpeg?auto=compress&cs=tinysrgb",
        "iconic_landmark": "Burj Khalifa"
    },

    # Australia & Oceania
    "sydney": {
        "name": "Sydney, Australia",
        "description": "Australia's harbor jewel, where the iconic Opera House meets golden beaches. Sydney offers world-class dining, stunning harbor views, vibrant neighborhoods, and easy access to both urban sophistication and natural beauty.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Australia",
        "region": "New South Wales",
        "country": "Australia",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1667896791269-05d7d0b6b5ae?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwyfHxsYW5kbWFya3xlbnwwfHx8fDE3NTQ0NDI0OTh8MA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Sydney Opera House"
    },
    "melbourne": {
        "name": "Melbourne, Australia",
        "description": "Australia's cultural capital, renowned for its coffee culture, street art, and hidden laneways. Melbourne offers world-class dining, vibrant arts scene, stunning gardens, and a European atmosphere in the heart of Australia.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Australia",
        "region": "Victoria",
        "country": "Australia",
        "hidden_gem": False,
        "image_url": "https://images.pexels.com/photos/775201/pexels-photo-775201.jpeg?auto=compress&cs=tinysrgb",
        "iconic_landmark": "Flinders Street Station"
    },
    "auckland": {
        "name": "Auckland, New Zealand",
        "description": "The City of Sails, where volcanic cones meet beautiful harbors. Auckland offers stunning natural beauty, Polynesian culture, world-class wineries, and easy access to both urban attractions and outdoor adventures.",
        "safety_rating": 4,
        "solo_female_rating": 4,
        "continent": "Australia",
        "region": "North Island",
        "country": "New Zealand",
        "hidden_gem": True,
        "image_url": "https://images.pexels.com/photos/3358880/pexels-photo-3358880.png?auto=compress&cs=tinysrgb",
        "iconic_landmark": "Sky Tower"
    },
    "queenstown": {
        "name": "Queenstown, New Zealand",
        "description": "The adventure capital of the world, nestled among dramatic alpine scenery. Queenstown offers thrilling outdoor activities, stunning lake and mountain views, world-class wineries, and breathtaking natural beauty at every turn.",
        "safety_rating": 5,
        "solo_female_rating": 5,
        "continent": "Australia",
        "region": "South Island",
        "country": "New Zealand",
        "hidden_gem": True,
        "image_url": "https://images.pexels.com/photos/2644325/pexels-photo-2644325.jpeg?auto=compress&cs=tinysrgb",
        "iconic_landmark": "Lake Wakatipu & The Remarkables"
    },

    # South America
    "rio_de_janeiro": {
        "name": "Rio de Janeiro, Brazil",
        "description": "The Marvelous City, where stunning beaches meet dramatic mountains and infectious carnival spirit. Rio captivates with its iconic Christ statue, world-famous Copacabana beach, vibrant samba culture, and breathtaking natural setting.",
        "safety_rating": 2,
        "solo_female_rating": 2,
        "continent": "South America",
        "region": "Southeast Brazil",
        "country": "Brazil",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw1fHxsYW5kbWFya3xlbnwwfHx8fDE3NTQ0NDI0OTh8MA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Christ the Redeemer"
    },
    "buenos_aires": {
        "name": "Buenos Aires, Argentina",
        "description": "The Paris of South America, where European elegance meets passionate Latin culture. Buenos Aires enchants with its tango-filled streets, incredible steakhouses, beautiful architecture, and vibrant neighborhood life.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "South America",
        "region": "Central Argentina",
        "country": "Argentina",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1589909202802-8f4aadce1849?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw2fHxsYW5kbWFya3xlbnwwfHx8fDE3NTQ0NDI0OTh8MA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Obelisco de Buenos Aires"
    },
    "lima": {
        "name": "Lima, Peru",
        "description": "South America's culinary capital, where ancient history meets world-class gastronomy. Lima offers incredible cuisine, colonial architecture, Pacific coastline, and serves as the gateway to Peru's amazing archaeological treasures.",
        "safety_rating": 2,
        "solo_female_rating": 2,
        "continent": "South America",
        "region": "Central Peru",
        "country": "Peru",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1531968455001-5c5272a41129?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw3fHxsYW5kbWFya3xlbnwwfHx8fDE3NTQ0NDI0OTh8MA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Historic Center of Lima"
    },
    "santiago": {
        "name": "Santiago, Chile",
        "description": "A modern capital surrounded by snow-capped Andes mountains and world-renowned wine valleys. Santiago offers excellent museums, vibrant neighborhoods, incredible wine culture, and easy access to both mountains and coast.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "South America",
        "region": "Central Chile",
        "country": "Chile",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1554995207-c18c203602cb?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw4fHxsYW5kbWFya3xlbnwwfHx8fDE3NTQ0NDI0OTh8MA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Cerro San Cristóbal"
    },
    "cartagena": {
        "name": "Cartagena, Colombia",
        "description": "A Caribbean colonial jewel where colorful architecture meets crystal-clear waters. Cartagena enchants with its UNESCO World Heritage old town, vibrant street life, incredible history, and romantic tropical atmosphere.",
        "safety_rating": 3,
        "solo_female_rating": 3,
        "continent": "South America",
        "region": "Caribbean Colombia",
        "country": "Colombia",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1564149504025-c4336a9bbc6b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHw5fHxsYW5kbWFya3xlbnwwfHx8fDE3NTQ0NDI0OTh8MA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Old Town Colonial Walls"
    },

    # Africa
    "cape_town": {
        "name": "Cape Town, South Africa",
        "description": "One of the world's most beautiful cities, where dramatic Table Mountain meets pristine beaches and world-class wine regions. Cape Town offers incredible natural beauty, rich history, vibrant culture, and stunning landscapes.",
        "safety_rating": 3,
        "solo_female_rating": 2,
        "continent": "Africa",
        "region": "Western Cape",
        "country": "South Africa",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxMHx8bGFuZG1hcmt8ZW58MHx8fHwxNzU0NDQyNDk4fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Table Mountain"
    },
    "marrakech": {
        "name": "Marrakech, Morocco",
        "description": "The Red City, where ancient medinas meet desert landscapes and vibrant souks. Marrakech offers an sensory adventure with its bustling markets, stunning palaces, traditional riads, and serves as gateway to the Sahara Desert.",
        "safety_rating": 3,
        "solo_female_rating": 2,
        "continent": "Africa",
        "region": "Central Morocco",
        "country": "Morocco",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1539650116574-75c0c6d68370?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxMXx8bGFuZG1hcmt8ZW58MHx8fHwxNzU0NDQyNDk4fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Koutoubia Mosque"
    },
    "cairo": {
        "name": "Cairo, Egypt",
        "description": "The Mother of the World, where ancient pyramids meet bustling modern city life along the Nile River. Cairo offers incredible archaeological treasures, rich Islamic architecture, vibrant bazaars, and thousands of years of history.",
        "safety_rating": 2,
        "solo_female_rating": 1,
        "continent": "Africa",
        "region": "Northern Egypt",
        "country": "Egypt",
        "hidden_gem": False,
        "image_url": "https://images.unsplash.com/photo-1539650116574-75c0c6d68370?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxMnx8bGFuZG1hcmt8ZW58MHx8fHwxNzU0NDQyNDk4fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Pyramids of Giza"
    },
    "nairobi": {
        "name": "Nairobi, Kenya",
        "description": "The safari capital of East Africa, where urban sophistication meets incredible wildlife experiences. Nairobi offers unique access to both city culture and amazing national parks, vibrant arts scene, and warm Kenyan hospitality.",
        "safety_rating": 2,
        "solo_female_rating": 2,
        "continent": "Africa",
        "region": "Central Kenya",
        "country": "Kenya",
        "hidden_gem": True,
        "image_url": "https://images.unsplash.com/photo-1544467284-2b5ac5a4b7fc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxM3x8bGFuZG1hcmt8ZW58MHx8fHwxNzU0NDQyNDk4fDA&ixlib=rb-4.1.0&q=85",
        "iconic_landmark": "Nairobi National Park"
    }
}

# Sample activities for each destination
SAMPLE_ACTIVITIES = {
    "paris": [
        {"name": "Louvre Museum", "category": "museums", "duration": "3-4 hours"},
        {"name": "Eiffel Tower", "category": "historic landmarks", "duration": "2 hours"},
        {"name": "Notre-Dame Cathedral", "category": "historic landmarks", "duration": "1 hour"},
        {"name": "Champs-Élysées Shopping", "category": "dining hot spots", "duration": "2-3 hours"},
        {"name": "Seine River Cruise", "category": "scenic drives", "duration": "1.5 hours"}
    ],
    "london": [
        {"name": "British Museum", "category": "museums", "duration": "3-4 hours"},
        {"name": "Tower of London", "category": "historic landmarks", "duration": "2-3 hours"},
        {"name": "Westminster Abbey", "category": "historic landmarks", "duration": "1.5 hours"},
        {"name": "Borough Market", "category": "dining hot spots", "duration": "1-2 hours"},
        {"name": "Thames River Walk", "category": "scenic drives", "duration": "2 hours"}
    ],
    "tokyo": [
        {"name": "Senso-ji Temple", "category": "historic landmarks", "duration": "2 hours"},
        {"name": "Tokyo National Museum", "category": "museums", "duration": "3 hours"},
        {"name": "Tsukiji Outer Market", "category": "dining hot spots", "duration": "2 hours"},
        {"name": "Imperial Palace Gardens", "category": "outdoor", "duration": "1.5 hours"},
        {"name": "Shibuya Crossing", "category": "family friendly", "duration": "1 hour"}
    ],
    "new_york": [
        {"name": "Metropolitan Museum of Art", "category": "museums", "duration": "3-4 hours"},
        {"name": "Central Park Walk", "category": "outdoor", "duration": "2-3 hours"},
        {"name": "Statue of Liberty", "category": "historic landmarks", "duration": "4 hours"},
        {"name": "Times Square Experience", "category": "family friendly", "duration": "2 hours"},
        {"name": "Chelsea Market Food Tour", "category": "dining hot spots", "duration": "2 hours"}
    ],
    "rome": [
        {"name": "Colosseum Tour", "category": "historic landmarks", "duration": "2-3 hours"},
        {"name": "Vatican Museums", "category": "museums", "duration": "3-4 hours"},
        {"name": "Trevi Fountain Visit", "category": "historic landmarks", "duration": "1 hour"},
        {"name": "Trastevere Food Tour", "category": "dining hot spots", "duration": "3 hours"},
        {"name": "Roman Forum Walk", "category": "historic landmarks", "duration": "2 hours"}
    ],
    "sydney": [
        {"name": "Sydney Opera House Tour", "category": "historic landmarks", "duration": "2 hours"},
        {"name": "Bondi Beach", "category": "beaches", "duration": "3-4 hours"},
        {"name": "Harbour Bridge Climb", "category": "outdoor", "duration": "3 hours"},
        {"name": "Royal Botanic Gardens", "category": "outdoor", "duration": "2 hours"},
        {"name": "The Rocks Market", "category": "dining hot spots", "duration": "2 hours"}
    ],
    "barcelona": [
        {"name": "Sagrada Familia", "category": "historic landmarks", "duration": "2 hours"},
        {"name": "Park Güell", "category": "outdoor", "duration": "2-3 hours"},
        {"name": "Gothic Quarter Walk", "category": "historic landmarks", "duration": "2 hours"},
        {"name": "La Boqueria Market", "category": "dining hot spots", "duration": "1-2 hours"},
        {"name": "Barceloneta Beach", "category": "beaches", "duration": "3 hours"}
    ],
    "amsterdam": [
        {"name": "Anne Frank House", "category": "museums", "duration": "2 hours"},
        {"name": "Canal Cruise", "category": "scenic drives", "duration": "1.5 hours"},
        {"name": "Van Gogh Museum", "category": "museums", "duration": "2-3 hours"},
        {"name": "Jordaan District Walk", "category": "outdoor", "duration": "2 hours"},
        {"name": "Albert Cuyp Market", "category": "dining hot spots", "duration": "1-2 hours"}
    ],
    "berlin": [
        {"name": "Brandenburg Gate", "category": "historic landmarks", "duration": "1 hour"},
        {"name": "Museum Island", "category": "museums", "duration": "4 hours"},
        {"name": "East Side Gallery", "category": "historic landmarks", "duration": "2 hours"},
        {"name": "Tiergarten Park", "category": "outdoor", "duration": "2-3 hours"},
        {"name": "Hackescher Markt Food Scene", "category": "dining hot spots", "duration": "2 hours"}
    ],
    "singapore": [
        {"name": "Gardens by the Bay", "category": "outdoor", "duration": "3 hours"},
        {"name": "Marina Bay Sands SkyPark", "category": "scenic drives", "duration": "1 hour"},
        {"name": "Chinatown Heritage Centre", "category": "museums", "duration": "1.5 hours"},
        {"name": "Hawker Center Food Tour", "category": "dining hot spots", "duration": "2 hours"},
        {"name": "Singapore Zoo", "category": "family friendly", "duration": "4 hours"}
    ]
}

# HTTP client for external APIs
http_client = httpx.AsyncClient(timeout=30.0)

@app.get("/")
async def root():
    return {
        "message": "Dream Travels API - Optimized Version",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "destinations": "/api/destinations", 
            "interests": "/api/interests",
            "theme_parks": "/api/theme-parks/queue-times"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Dream Travels API is running"
    }

@app.get("/api/destinations")
async def get_destinations(
    region: str = None,
    city: str = None, 
    solo_female_safe: bool = False,
    hidden_gems: bool = False
):
    filtered_destinations = {}
    
    for key, destination in DESTINATIONS.items():
        # Apply filters
        include_destination = True
        
        # Region filter (map frontend regions to backend continents)
        if region:
            region_mapping = {
                "North America": "North America",
                "Europe": "Europe", 
                "Asia": "Asia",
                "Australia": "Australia",
                "South America": "South America",
                "Africa": "Africa"
            }
            expected_continent = region_mapping.get(region)
            if expected_continent and destination.get("continent") != expected_continent:
                include_destination = False
        
        # City filter (partial name matching)
        if city and city.lower() != "all cities":
            if city.lower() not in destination.get("name", "").lower():
                include_destination = False
        
        # Solo female safe filter (4+ rating)
        if solo_female_safe:
            if destination.get("solo_female_rating", 0) < 4:
                include_destination = False
                
        # Hidden gems filter
        if hidden_gems:
            if not destination.get("hidden_gem", False):
                include_destination = False
        
        if include_destination:
            filtered_destinations[key] = destination
    
    return {
        "destinations": filtered_destinations,
        "count": len(filtered_destinations),
        "message": f"Available destinations for travel planning (filtered: {len(filtered_destinations)} of {len(DESTINATIONS)})"
    }

@app.get("/api/interests")
async def get_interests():
    interests = [
        "scenic drives", "hikes", "beaches", "theme parks", "museums",
        "historic landmarks", "family friendly", "dining hot spots", 
        "outdoor", "solo female"
    ]
    return {
        "interests": interests,
        "solo_female_notes": "Destinations with safety ratings 3+ recommended for solo female travelers"
    }

@app.post("/api/generate-itinerary") 
async def generate_itinerary(request: dict):
    destination = request.get("destination", "").lower().replace(" ", "_").replace(",", "")
    interests = request.get("interests", [])
    number_of_days = request.get("number_of_days", 3)
    
    # Find destination
    dest_key = None
    for key in DESTINATIONS.keys():
        if destination in key or key in destination:
            dest_key = key
            break
    
    if not dest_key:
        return {"error": f"Destination not found. Available: {list(DESTINATIONS.keys())}"}
    
    # Get activities for destination
    activities = SAMPLE_ACTIVITIES.get(dest_key, [])
    
    # Filter by interests
    filtered_activities = []
    for activity in activities:
        if any(interest.lower() in activity["category"].lower() for interest in interests):
            filtered_activities.append({
                "id": f"{dest_key}_{activity['name'].replace(' ', '_').lower()}",
                "name": activity["name"],
                "category": activity["category"],
                "description": f"Experience {activity['name']} in {DESTINATIONS[dest_key]['name']}",
                "estimated_duration": activity["duration"],
                "best_time": "Morning or afternoon",
                "location": {"lat": 0.0, "lng": 0.0},
                "address": DESTINATIONS[dest_key]['name']
            })
    
    # Create day-by-day itinerary
    days = []
    activities_per_day = max(1, len(filtered_activities) // number_of_days)
    
    for day in range(1, number_of_days + 1):
        start_idx = (day - 1) * activities_per_day
        end_idx = start_idx + activities_per_day
        day_activities = filtered_activities[start_idx:end_idx]
        
        days.append({
            "day": day,
            "title": f"Day {day} in {DESTINATIONS[dest_key]['name']}",
            "activities": day_activities
        })
    
    return {
        "id": f"itinerary_{dest_key}_{datetime.utcnow().strftime('%Y%m%d')}",
        "destination": DESTINATIONS[dest_key]['name'],
        "interests": interests,
        "number_of_days": number_of_days,
        "days": days,
        "total_activities": len(filtered_activities),
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/api/theme-parks/queue-times")
async def get_theme_parks():
    try:
        # Try to get real data from Queue Times API
        response = await http_client.get("https://queue-times.com/parks.json")
        if response.status_code == 200:
            parks_data = response.json()
            parks = []
            for company in parks_data[:5]:  # Limit to prevent timeout
                company_parks = company.get("parks", [])[:10]  # Limit parks per company
                for park in company_parks:
                    parks.append({
                        "id": str(park.get("id", "")),
                        "name": park.get("name", "Unknown Park"),
                        "country": park.get("country", ""),
                        "source": "queue-times"
                    })
            
            return {
                "parks": parks,
                "total_parks": len(parks),
                "source": "queue-times.com",
                "message": "Live theme park data"
            }
    except Exception as e:
        pass
    
    # Fallback data
    return {
        "parks": [
            {"id": "6", "name": "Magic Kingdom", "country": "United States", "source": "queue-times"},
            {"id": "7", "name": "Disney's Hollywood Studios", "country": "United States", "source": "queue-times"},
            {"id": "8", "name": "EPCOT", "country": "United States", "source": "queue-times"}
        ],
        "total_parks": 3,
        "source": "fallback-data",
        "message": "Limited theme park data available"
    }

@app.get("/api/theme-parks/{park_id}/wait-times")
async def get_park_wait_times(park_id: str):
    try:
        # Try to get real wait times
        response = await http_client.get(f"https://queue-times.com/parks/{park_id}/queue_times.json")
        if response.status_code == 200:
            data = response.json()
            attractions = []
            
            for land in data.get("lands", [])[:3]:  # Limit lands
                for ride in land.get("rides", [])[:5]:  # Limit rides per land
                    attractions.append({
                        "id": str(ride.get("id", "")),
                        "name": ride.get("name", "Unknown Ride"),
                        "wait_time": ride.get("wait_time", 0),
                        "is_open": ride.get("is_open", False),
                        "land": land.get("name", "Unknown Land")
                    })
            
            return {
                "park_id": park_id,
                "attractions": attractions,
                "total_attractions": len(attractions),
                "source": "queue-times-live"
            }
    except Exception as e:
        pass
    
    # Fallback data
    return {
        "park_id": park_id,
        "attractions": [
            {"id": "1", "name": "Space Mountain", "wait_time": 45, "is_open": True, "land": "Tomorrowland"},
            {"id": "2", "name": "Pirates of the Caribbean", "wait_time": 20, "is_open": True, "land": "Adventureland"},
            {"id": "3", "name": "Haunted Mansion", "wait_time": 35, "is_open": True, "land": "Liberty Square"}
        ],
        "total_attractions": 3,
        "source": "fallback-data"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)