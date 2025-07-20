import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CrowdLevelBadge = ({ level, description }) => {
  const getColor = (level) => {
    if (level <= 2) return "bg-green-500 text-white";
    if (level <= 4) return "bg-yellow-500 text-white";
    if (level <= 6) return "bg-orange-500 text-white";
    if (level <= 8) return "bg-red-500 text-white";
    return "bg-purple-500 text-white";
  };

  const getIcon = (level) => {
    if (level <= 2) return "😊";
    if (level <= 4) return "🙂";
    if (level <= 6) return "😐";
    if (level <= 8) return "😰";
    return "🚫";
  };

  return (
    <div className="flex items-center space-x-2">
      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getColor(level)}`}>
        {getIcon(level)} {description} ({level}/10)
      </span>
    </div>
  );
};

const AttractionCard = ({ attraction, isSelected, onToggle, waitTime, tips }) => (
  <div 
    className={`p-4 border-2 rounded-xl cursor-pointer transition-all duration-200 ${
      isSelected 
        ? "border-blue-500 bg-blue-50 shadow-lg" 
        : "border-gray-200 hover:border-blue-300 hover:shadow-md"
    }`}
    onClick={() => onToggle(attraction.id)}
  >
    <div className="flex items-start justify-between mb-3">
      <div className="flex-1">
        <h4 className="font-bold text-lg mb-1">{attraction.name}</h4>
        <div className="flex items-center space-x-3 mb-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            attraction.thrill_level === 'FAMILY' ? 'bg-green-100 text-green-800' :
            attraction.thrill_level === 'MODERATE' ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {attraction.thrill_level === 'FAMILY' ? '👨‍👩‍👧‍👦' : 
             attraction.thrill_level === 'MODERATE' ? '🎢' : '🚀'} 
            {attraction.thrill_level}
          </span>
          {attraction.fastpass_available && (
            <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
              ⚡ FastPass
            </span>
          )}
        </div>
      </div>
      <div className="text-right">
        <div className="text-2xl font-bold text-blue-600 mb-1">
          {waitTime || attraction.current_wait}min
        </div>
        <div className="text-xs text-gray-500">
          Avg: {Math.round(attraction.historical_average)}min
        </div>
      </div>
    </div>

    {attraction.height_requirement && (
      <div className="flex items-center text-sm text-orange-600 mb-2">
        📏 Height: {attraction.height_requirement}
      </div>
    )}

    <div className={`flex items-center text-sm mb-2 ${
      attraction.status === 'OPERATIONAL' ? 'text-green-600' : 'text-red-600'
    }`}>
      {attraction.status === 'OPERATIONAL' ? '✅' : '❌'} {attraction.status}
    </div>

    {tips && tips.length > 0 && (
      <div className="mt-3 p-2 bg-yellow-50 rounded-lg">
        <div className="text-sm font-medium text-yellow-800 mb-1">💡 Tips:</div>
        {tips.map((tip, index) => (
          <div key={index} className="text-xs text-yellow-700">• {tip}</div>
        ))}
      </div>
    )}

    {isSelected && (
      <div className="mt-3 text-center">
        <span className="inline-block px-3 py-1 bg-blue-500 text-white rounded-full text-sm font-semibold">
          ✓ Selected
        </span>
      </div>
    )}
  </div>
);

const OptimizedPlan = ({ plan, onBack }) => (
  <div className="space-y-6">
    <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">🎯 Your Optimized Theme Park Plan</h2>
        <button 
          onClick={onBack}
          className="px-4 py-2 bg-white bg-opacity-20 rounded-lg hover:bg-opacity-30 transition-colors"
        >
          ← Back to Edit
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold">{plan.total_attractions}</div>
          <div className="text-purple-100">Attractions</div>
        </div>
        <div className="text-center">
          <CrowdLevelBadge 
            level={plan.crowd_level} 
            description={plan.crowd_level <= 3 ? 'Light' : plan.crowd_level <= 6 ? 'Moderate' : 'Heavy'} 
          />
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold">{plan.estimated_total_time}</div>
          <div className="text-purple-100">Total Time</div>
        </div>
      </div>
    </div>

    {/* Optimized Schedule */}
    <div className="bg-white rounded-xl shadow-xl overflow-hidden">
      <div className="bg-gradient-to-r from-green-500 to-teal-500 px-6 py-4">
        <h3 className="text-xl font-bold text-white">📅 Your Schedule for {plan.visit_date}</h3>
      </div>
      
      <div className="p-6 space-y-4">
        {plan.plan.map((item, index) => (
          <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full flex items-center justify-center text-lg font-bold">
                {item.order}
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h4 className="font-bold text-lg">{item.attraction.name}</h4>
                  <div className="flex items-center space-x-3 mt-1">
                    <span className="text-blue-600 font-semibold">🕒 {item.recommended_time}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      item.attraction.thrill_level === 'FAMILY' ? 'bg-green-100 text-green-800' :
                      item.attraction.thrill_level === 'MODERATE' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {item.attraction.thrill_level}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xl font-bold text-orange-600">{item.estimated_wait}min</div>
                  <div className="text-xs text-gray-500">Est. Wait</div>
                </div>
              </div>
              
              {item.tips && item.tips.length > 0 && (
                <div className="mt-2 p-2 bg-blue-50 rounded">
                  {item.tips.map((tip, tipIndex) => (
                    <div key={tipIndex} className="text-xs text-blue-700">💡 {tip}</div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>

    {/* General Tips */}
    <div className="bg-white rounded-xl shadow-xl p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">🎯 General Tips for Your Visit</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {plan.general_tips.map((tip, index) => (
          <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
            <span className="text-green-600 text-sm">✅</span>
            <span className="text-sm text-gray-700">{tip}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

function ThemeParkPlanner() {
  const [step, setStep] = useState('parks'); // parks, attractions, plan
  const [availableParks, setAvailableParks] = useState([]);
  const [selectedPark, setSelectedPark] = useState(null);
  const [parkDetails, setParkDetails] = useState(null);
  const [attractions, setAttractions] = useState([]);
  const [selectedAttractions, setSelectedAttractions] = useState([]);
  const [visitDate, setVisitDate] = useState(new Date().toISOString().split('T')[0]);
  const [arrivalTime, setArrivalTime] = useState('08:00');
  const [loading, setLoading] = useState(false);
  const [optimizedPlan, setOptimizedPlan] = useState(null);
  const [waitTimes, setWaitTimes] = useState({});
  const [crowdPrediction, setCrowdPrediction] = useState(null);

  // Load available theme parks
  useEffect(() => {
    const loadParks = async () => {
      try {
        const response = await axios.get(`${API}/theme-parks/parks`);
        setAvailableParks(response.data.parks);
      } catch (error) {
        console.error('Error loading theme parks:', error);
      }
    };
    loadParks();
  }, []);

  // Load park details when park is selected
  useEffect(() => {
    if (selectedPark) {
      const loadParkDetails = async () => {
        try {
          setLoading(true);
          const [detailsResponse, waitTimesResponse] = await Promise.all([
            axios.get(`${API}/theme-parks/parks/${selectedPark.id}`),
            axios.get(`${API}/theme-parks/parks/${selectedPark.id}/wait-times`)
          ]);
          
          setParkDetails(detailsResponse.data);
          setAttractions(detailsResponse.data.park.attractions);
          setWaitTimes(waitTimesResponse.data);
        } catch (error) {
          console.error('Error loading park details:', error);
        } finally {
          setLoading(false);
        }
      };
      loadParkDetails();
    }
  }, [selectedPark]);

  // Load crowd prediction when date changes
  useEffect(() => {
    if (selectedPark && visitDate) {
      const loadCrowdPrediction = async () => {
        try {
          const response = await axios.get(`${API}/theme-parks/parks/${selectedPark.id}/crowds/${visitDate}`);
          setCrowdPrediction(response.data);
        } catch (error) {
          console.error('Error loading crowd prediction:', error);
        }
      };
      loadCrowdPrediction();
    }
  }, [selectedPark, visitDate]);

  const handleParkSelect = (park) => {
    setSelectedPark(park);
    setStep('attractions');
  };

  const handleAttractionToggle = (attractionId) => {
    setSelectedAttractions(prev => 
      prev.includes(attractionId) 
        ? prev.filter(id => id !== attractionId)
        : [...prev, attractionId]
    );
  };

  const generateOptimizedPlan = async () => {
    if (selectedAttractions.length === 0) {
      alert('Please select at least one attraction!');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/theme-parks/parks/${selectedPark.id}/optimize-plan`, {
        park_id: selectedPark.id,
        selected_attractions: selectedAttractions,
        visit_date: visitDate,
        arrival_time: arrivalTime
      });
      
      setOptimizedPlan(response.data);
      setStep('plan');
    } catch (error) {
      console.error('Error generating optimized plan:', error);
      alert('Error generating plan. Please try again!');
    } finally {
      setLoading(false);
    }
  };

  const resetPlanner = () => {
    setStep('parks');
    setSelectedPark(null);
    setSelectedAttractions([]);
    setOptimizedPlan(null);
  };

  if (step === 'plan' && optimizedPlan) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-6">
        <div className="max-w-6xl mx-auto">
          <OptimizedPlan plan={optimizedPlan} onBack={() => setStep('attractions')} />
          <div className="text-center mt-8">
            <button
              onClick={resetPlanner}
              className="px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all duration-200"
            >
              🎢 Plan Another Park Visit
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-12">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">🎢 Theme Park Planner</h1>
          <p className="text-xl text-purple-100">
            Optimize your theme park experience with real-time crowd predictions and wait times
          </p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Step 1: Park Selection */}
        {step === 'parks' && (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">Choose Your Theme Park</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {availableParks.map(park => (
                <div 
                  key={park.id}
                  className="bg-white rounded-xl shadow-xl overflow-hidden cursor-pointer hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
                  onClick={() => handleParkSelect(park)}
                >
                  <div className="p-6">
                    <h3 className="text-xl font-bold mb-2">{park.name}</h3>
                    <p className="text-gray-600 mb-4">📍 {park.location}</p>
                    
                    <div className="space-y-3">
                      <CrowdLevelBadge level={park.current_crowd_level} description={park.crowd_description} />
                      
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>🎢 {park.total_attractions} attractions</span>
                        <span>🕒 {park.timezone}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-purple-500 to-blue-500 px-6 py-3 text-center">
                    <span className="text-white font-semibold">Select This Park →</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Attraction Selection */}
        {step === 'attractions' && selectedPark && (
          <div className="space-y-6">
            {/* Park Header */}
            <div className="bg-white rounded-xl shadow-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold">{selectedPark.name}</h2>
                  <p className="text-gray-600">{selectedPark.location}</p>
                </div>
                <button 
                  onClick={() => setStep('parks')}
                  className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  ← Change Park
                </button>
              </div>

              {crowdPrediction && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-blue-50 rounded-lg">
                  <div>
                    <CrowdLevelBadge level={crowdPrediction.crowd_index} description={crowdPrediction.crowd_description} />
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1">Best Times:</div>
                    <div className="text-xs text-green-700">
                      {crowdPrediction.best_visit_times.join(', ')}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1">Avoid:</div>
                    <div className="text-xs text-red-700">
                      {crowdPrediction.peak_times.join(', ')}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Date and Time Selection */}
            <div className="bg-white rounded-xl shadow-xl p-6">
              <h3 className="text-xl font-bold mb-4">📅 Plan Your Visit</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Visit Date</label>
                  <input
                    type="date"
                    value={visitDate}
                    onChange={(e) => setVisitDate(e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Arrival Time</label>
                  <select
                    value={arrivalTime}
                    onChange={(e) => setArrivalTime(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="08:00">8:00 AM (Rope Drop)</option>
                    <option value="09:00">9:00 AM</option>
                    <option value="10:00">10:00 AM</option>
                    <option value="11:00">11:00 AM</option>
                    <option value="12:00">12:00 PM</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Attraction Selection */}
            <div className="bg-white rounded-xl shadow-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold">🎢 Select Attractions ({selectedAttractions.length} selected)</h3>
                {selectedAttractions.length > 0 && (
                  <button
                    onClick={generateOptimizedPlan}
                    disabled={loading}
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200 disabled:opacity-50"
                  >
                    {loading ? 'Optimizing...' : '✨ Generate Plan'}
                  </button>
                )}
              </div>

              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Loading attractions...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {attractions.map(attraction => {
                    const waitTimeData = waitTimes.attractions?.find(wt => wt.id === attraction.id);
                    return (
                      <AttractionCard
                        key={attraction.id}
                        attraction={attraction}
                        isSelected={selectedAttractions.includes(attraction.id)}
                        onToggle={handleAttractionToggle}
                        waitTime={waitTimeData?.current_wait}
                        tips={waitTimeData?.tips}
                      />
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ThemeParkPlanner;