import React, { useState } from "react";
import "./App.css";
import EnhancedApp from "./EnhancedApp";
import ThemeParkPlanner from "./components/ThemeParkPlanner";

function App() {
  const [currentApp, setCurrentApp] = useState(null); // null, 'travel', or 'themepark'

  const AppSelector = () => (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100">
      <div className="bg-gradient-to-r from-indigo-600 to-purple-700 text-white py-16">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">Dream Travels</h1>
          <p className="text-xl md:text-2xl mb-8">
            Your ultimate travel companion with itinerary planning and theme park optimization
          </p>
        </div>
      </div>
      
      <div className="max-w-4xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Travel Itinerary Planner */}
          <div 
            className="bg-white rounded-2xl shadow-xl p-8 cursor-pointer hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
            onClick={() => setCurrentApp('travel')}
          >
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-3xl mx-auto mb-6">
                🗺️
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Travel Itinerary Builder</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Create personalized travel itineraries with 50+ global destinations, solo female safety guides, and hidden gems from 6 continents.
              </p>
              <div className="space-y-2 text-sm text-gray-500 mb-6">
                <div className="flex items-center justify-center space-x-2">
                  <span>🌍</span><span>50+ Destinations</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <span>👩</span><span>Solo Female Safety</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <span>💎</span><span>Hidden Gems</span>
                </div>
              </div>
              <button className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200">
                Start Planning →
              </button>
            </div>
          </div>

          {/* Theme Park Planner */}
          <div 
            className="bg-white rounded-2xl shadow-xl p-8 cursor-pointer hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
            onClick={() => setCurrentApp('themepark')}
          >
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center text-3xl mx-auto mb-6">
                🎢
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Theme Park Optimizer</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Optimize your theme park experience with real-time crowd predictions, wait times, and personalized touring plans for Disney, Universal & more.
              </p>
              <div className="space-y-2 text-sm text-gray-500 mb-6">
                <div className="flex items-center justify-center space-x-2">
                  <span>📊</span><span>Real-time Wait Times</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <span>🔮</span><span>Crowd Predictions</span>
                </div>
                <div className="flex items-center justify-center space-x-2">
                  <span>⚡</span><span>FastPass Integration</span>
                </div>
              </div>
              <button className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white font-bold rounded-xl hover:from-purple-600 hover:to-pink-700 transition-all duration-200">
                Optimize My Visit →
              </button>
            </div>
          </div>
        </div>
        
        <div className="text-center mt-12">
          <p className="text-gray-500">
            🚀 <strong>NEW:</strong> Theme Park Planner with crowd prediction technology powered by thrill-data.com
          </p>
        </div>
      </div>
    </div>
  );

  if (currentApp === 'travel') {
    return (
      <div>
        <div className="fixed top-4 left-4 z-50">
          <button
            onClick={() => setCurrentApp(null)}
            className="px-4 py-2 bg-white bg-opacity-90 text-gray-700 rounded-lg shadow-lg hover:bg-opacity-100 transition-all duration-200 font-semibold"
          >
            ← Back to Apps
          </button>
        </div>
        <EnhancedApp />
      </div>
    );
  }

  if (currentApp === 'themepark') {
    return (
      <div>
        <div className="fixed top-4 left-4 z-50">
          <button
            onClick={() => setCurrentApp(null)}
            className="px-4 py-2 bg-white bg-opacity-90 text-gray-700 rounded-lg shadow-lg hover:bg-opacity-100 transition-all duration-200 font-semibold"
          >
            ← Back to Apps
          </button>
        </div>
        <ThemeParkPlanner />
      </div>
    );
  }

  return <AppSelector />;
}

export default App;