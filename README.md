# Dream Travels - Your Ultimate Travel Planning Companion

Dream Travels is a comprehensive full-stack travel planning application that helps you create perfect itineraries and optimize theme park visits.

## 🌟 Features

### Travel Itinerary Builder
- **50+ Global Destinations** with safety ratings and local insights
- **Solo Female Travel** features with safety ratings and tips
- **Interest-Based Planning** (museums, outdoor activities, dining, theme parks, etc.)
- **Geographic Clustering** for efficient day-by-day itineraries
- **Custom Activities** - Add your own places of interest
- **Travel Blog Integration** - Real content from travel experts

### Theme Park Optimizer
- **178 Theme Parks Worldwide** (133 from Queue Times + 45 from WaitTimesApp)
- **Real-Time Wait Times** updated every 5 minutes
- **Crowd Predictions** with best visit times
- **Optimized Touring Plans** based on current conditions
- **Global Coverage** - US parks (Disney, Universal) + European parks (Alton Towers, Europa-Park)

## 🛠 Technology Stack

- **Frontend**: React 19 with Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: MongoDB
- **APIs**: 
  - Queue Times API (133 theme parks)
  - WaitTimesApp API (45 international parks)
  - Travel blog scraping from multiple sources

## 🚀 Getting Started

### Prerequisites
- Node.js and yarn
- Python 3.11+
- MongoDB

### Installation
1. Clone the repository
2. Install frontend dependencies: `cd frontend && yarn install`
3. Install backend dependencies: `cd backend && pip install -r requirements.txt`
4. Start the development servers:
   - Frontend: `yarn start` (port 3000)
   - Backend: `uvicorn enhanced_server:app --reload --port 8001`

## 🌍 API Coverage

- **Queue Times**: 133 parks (Disney World, Disneyland, Universal Studios, Cedar Fair, Six Flags, SeaWorld)
- **WaitTimesApp**: 45 parks (Alton Towers, Europa-Park, Phantasialand, Efteling, etc.)
- **Travel Blogs**: Global destinations with real content from travel experts

## 📱 Features in Detail

### Smart Itinerary Generation
- Analyzes your interests and creates day-by-day plans
- Groups activities geographically for efficient travel
- Includes dining recommendations and local tips
- Provides safety information for solo travelers

### Real-Time Theme Park Data
- Live wait times updated every 5 minutes
- Crowd level predictions and recommendations
- Attraction status (operational, closed, maintenance)
- Optimized touring plans based on current conditions

## 🔧 Configuration

The app uses environment variables for configuration:
- `MONGO_URL`: MongoDB connection string
- `REACT_APP_BACKEND_URL`: Backend API URL

## 🎯 Built for Travelers

Whether you're planning a cultural trip to Paris, a family vacation to Disney World, or an adventure through European theme parks, Dream Travels provides the data and tools you need to make the most of your journey.

## 📄 License

Built with ❤️ using Emergent platform
