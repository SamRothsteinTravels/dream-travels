import React, { useState, useEffect, useCallback } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HERO_IMAGE = "https://images.unsplash.com/photo-1615826932727-ed9f182ac67e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwxfHx0cmF2ZWwlMjBwbGFubmluZ3xlbnwwfHx8fDE3NTMwMzU0NTd8MA&ixlib=rb-4.1.0&q=85";

const SafetyBadge = ({ rating, notes }) => {
  const colors = {
    5: "bg-green-500 text-white",
    4: "bg-blue-500 text-white", 
    3: "bg-yellow-500 text-white",
    2: "bg-orange-500 text-white",
    1: "bg-red-500 text-white"
  };

  const labels = {
    5: "Extremely Safe",
    4: "Very Safe",
    3: "Moderately Safe", 
    2: "Caution Advised",
    1: "High Risk"
  };

  return (
    <div className="flex items-center space-x-2 mb-2">
      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${colors[rating]}`}>
        👩 {labels[rating]} ({rating}/5)
      </span>
      {notes && (
        <div className="group relative">
          <span className="text-blue-500 cursor-help">ℹ️</span>
          <div className="absolute bottom-full left-0 mb-2 w-64 p-2 bg-gray-800 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity z-10">
            {notes}
          </div>
        </div>
      )}
    </div>
  );
};

const DestinationCard = ({ destination, onSelect, selected }) => (
  <div 
    className={`p-4 border-2 rounded-xl cursor-pointer transition-all duration-200 ${
      selected 
        ? "border-blue-500 bg-blue-50 shadow-lg" 
        : "border-gray-200 hover:border-blue-300 hover:shadow-md"
    }`}
    onClick={() => onSelect(destination)}
  >
    <div className="flex items-start justify-between mb-2">
      <div>
        <h3 className="font-bold text-lg">{destination.name}</h3>
        <p className="text-gray-600">{destination.country} • {destination.region}</p>
        {destination.hidden_gem && (
          <span className="inline-block px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full mt-1">
            💎 Hidden Gem
          </span>
        )}
      </div>
    </div>
    <SafetyBadge rating={destination.solo_female_safety} notes={destination.safety_notes} />
    <p className="text-sm text-gray-700 leading-relaxed">{destination.description}</p>
  </div>
);

const FilterSection = ({ filters, onFiltersChange, citiesAndRegions }) => (
  <div className="bg-gray-50 p-6 rounded-xl mb-6">
    <h3 className="text-lg font-semibold mb-4">🔍 Filters</h3>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Region Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Region</label>
        <select 
          value={filters.region || ""} 
          onChange={(e) => onFiltersChange({...filters, region: e.target.value || null})}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Regions</option>
          <option value="North America">North America</option>
          <option value="Europe">Europe</option>
          <option value="Asia">Asia</option>
          <option value="South America">South America</option>
          <option value="Australia/Oceania">Australia/Oceania</option>
        </select>
      </div>

      {/* City/Area Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">City or Area</label>
        <select 
          value={filters.city || ""} 
          onChange={(e) => onFiltersChange({...filters, city: e.target.value || null})}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Cities</option>
          {citiesAndRegions.popular_cities?.map(city => (
            <option key={city.key} value={city.name.split(",")[0]}>
              {city.name} ({city.safety_rating}/5 ⭐)
            </option>
          ))}
        </select>
      </div>
    </div>

    {/* Special Options */}
    <div className="mt-4">
      <div className="space-y-2">
        <label className="flex items-center">
          <input 
            type="checkbox" 
            checked={filters.hidden_gems || false}
            onChange={(e) => onFiltersChange({...filters, hidden_gems: e.target.checked})}
            className="mr-2"
          />
          <span className="text-sm">💎 Hidden Gems Only</span>
        </label>
        <label className="flex items-center">
          <input 
            type="checkbox" 
            checked={filters.solo_female_safe || false}
            onChange={(e) => onFiltersChange({...filters, solo_female_safe: e.target.checked})}
            className="mr-2"
          />
          <span className="text-sm">👩 Solo Female Safe (4+ Rating)</span>
        </label>
      </div>
    </div>
  </div>
);

function EnhancedApp() {
  const [currentStep, setCurrentStep] = useState('destinations'); // destinations, interests, dates, itinerary
  const [destinations, setDestinations] = useState([]);
  const [filteredDestinations, setFilteredDestinations] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState(null);
  const [availableInterests, setAvailableInterests] = useState([]);
  const [selectedInterests, setSelectedInterests] = useState([]);
  const [travelDates, setTravelDates] = useState([]);
  const [numberOfDays, setNumberOfDays] = useState("");
  const [useDates, setUseDates] = useState(false);
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const [soloFemaleTraveler, setSoloFemaleTraveler] = useState(false);
  const [budgetRange, setBudgetRange] = useState("");
  const [citiesAndRegions, setCitiesAndRegions] = useState({ popular_cities: [] });
  
  // New state for custom activities
  const [customActivities, setCustomActivities] = useState([]);
  const [newCustomActivity, setNewCustomActivity] = useState({
    name: "",
    location: "",
    description: "",
    category: "custom",
    priority: 3
  });

  // Fetch destinations with filters
  const fetchDestinations = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (filters.region) params.append('region', filters.region);
      if (filters.city) params.append('city', filters.city);
      if (filters.solo_female_safe) params.append('solo_female_safe', 'true');
      if (filters.hidden_gems) params.append('hidden_gems', 'true');

      const response = await axios.get(`${API}/destinations?${params.toString()}`);
      setDestinations(response.data.destinations);
      setFilteredDestinations(response.data.destinations);
    } catch (error) {
      console.error("Error fetching destinations:", error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Fetch cities and regions data
  const fetchCitiesAndRegions = async () => {
    try {
      const response = await axios.get(`${API}/cities-and-regions`);
      setCitiesAndRegions(response.data);
    } catch (error) {
      console.error("Error fetching cities and regions:", error);
    }
  };

  // Fetch available interests
  const fetchInterests = async () => {
    try {
      const response = await axios.get(`${API}/interests`);
      setAvailableInterests(response.data.interests);
    } catch (error) {
      console.error("Error fetching interests:", error);
    }
  };

  useEffect(() => {
    fetchDestinations();
    fetchInterests();
    fetchCitiesAndRegions();
  }, [fetchDestinations]);

  const handleDestinationSelect = (destination) => {
    setSelectedDestination(destination);
  };

  const handleInterestToggle = (interest) => {
    setSelectedInterests(prev => 
      prev.includes(interest)
        ? prev.filter(i => i !== interest)
        : [...prev, interest]
    );
  };

  const handleDateChange = (index, value) => {
    const newDates = [...travelDates];
    newDates[index] = value;
    setTravelDates(newDates);
  };

  const addDate = () => {
    setTravelDates([...travelDates, ""]);
  };

  const removeDate = (index) => {
    setTravelDates(travelDates.filter((_, i) => i !== index));
  };

  // Custom activity management functions
  const addCustomActivity = () => {
    if (!newCustomActivity.name.trim() || !newCustomActivity.location.trim()) {
      alert('Please provide both name and location for the custom activity!');
      return;
    }
    
    setCustomActivities(prev => [...prev, { ...newCustomActivity, id: Date.now().toString() }]);
    setNewCustomActivity({
      name: "",
      location: "",
      description: "",
      category: "custom",
      priority: 3
    });
  };

  const removeCustomActivity = (id) => {
    setCustomActivities(prev => prev.filter(activity => activity.id !== id));
  };

  const updateCustomActivity = (field, value) => {
    setNewCustomActivity(prev => ({ ...prev, [field]: value }));
  };

  const generateItinerary = async () => {
    if (!selectedDestination || selectedInterests.length === 0) {
      alert("Please select a destination and at least one interest!");
      return;
    }

    if (!useDates && !numberOfDays) {
      alert("Please specify either travel dates or number of days!");
      return;
    }

    if (useDates && travelDates.filter(date => date).length === 0) {
      alert("Please provide at least one travel date!");
      return;
    }

    setLoading(true);
    try {
      const requestData = {
        destination: selectedDestination.name,
        interests: selectedInterests,
        travel_dates: useDates ? travelDates.filter(date => date) : null,
        number_of_days: useDates ? null : parseInt(numberOfDays),
        solo_female_traveler: soloFemaleTraveler,
        budget_range: budgetRange || null
      };

      const response = await axios.post(`${API}/generate-itinerary`, requestData);
      setItinerary(response.data);
      setCurrentStep('itinerary');
    } catch (error) {
      console.error("Error generating itinerary:", error);
      alert("Error generating itinerary. Please try again!");
    } finally {
      setLoading(false);
    }
  };

  const resetApp = () => {
    setCurrentStep('destinations');
    setSelectedDestination(null);
    setSelectedInterests([]);
    setTravelDates([]);
    setNumberOfDays("");
    setItinerary(null);
    setUseDates(false);
    setSoloFemaleTraveler(false);
    setBudgetRange("");
    setFilters({});
  };

  const nextStep = () => {
    if (currentStep === 'destinations' && selectedDestination) {
      setCurrentStep('interests');
    } else if (currentStep === 'interests' && selectedInterests.length > 0) {
      setCurrentStep('dates');
    }
  };

  const prevStep = () => {
    if (currentStep === 'interests') {
      setCurrentStep('destinations');
    } else if (currentStep === 'dates') {
      setCurrentStep('interests');
    } else if (currentStep === 'itinerary') {
      setCurrentStep('dates');
    }
  };

  const exportItinerary = async (format) => {
    try {
      await axios.post(`${API}/export-itinerary`, {
        itinerary_id: itinerary.id,
        format: format
      });
      alert(`Itinerary exported in ${format} format!`);
    } catch (error) {
      console.error("Export error:", error);
      alert("Export failed. Please try again!");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Enhanced Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-700">
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{ backgroundImage: `url(${HERO_IMAGE})` }}
        ></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              TravelMate Pro
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 mb-8 max-w-4xl mx-auto">
              Discover the world safely with personalized itineraries, solo female traveler guides, 
              and hidden gems from 6 continents
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-blue-100">
              <span className="flex items-center">
                <span className="mr-2">🌍</span> 50+ Destinations
              </span>
              <span className="flex items-center">
                <span className="mr-2">💎</span> Hidden Gems
              </span>
              <span className="flex items-center">
                <span className="mr-2">👩</span> Solo Female Safe
              </span>
              <span className="flex items-center">
                <span className="mr-2">🗺️</span> Smart Clustering
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            {['destinations', 'interests', 'dates', 'itinerary'].map((step, index) => (
              <div key={step} className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold ${
                  currentStep === step ? 'bg-blue-500 text-white' :
                  ['destinations', 'interests', 'dates'].indexOf(currentStep) > index ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
                }`}>
                  {index + 1}
                </div>
                <span className="ml-2 text-sm font-medium capitalize hidden sm:inline">
                  {step === 'destinations' ? 'Choose Destination' : 
                   step === 'interests' ? 'Select Interests' :
                   step === 'dates' ? 'Set Dates' : 'Your Itinerary'}
                </span>
                {index < 3 && <div className="w-8 h-1 bg-gray-300 mx-4 hidden sm:block"></div>}
              </div>
            ))}
          </div>
        </div>

        {/* Step 1: Destination Selection */}
        {currentStep === 'destinations' && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
              🌍 Choose Your Destination
            </h2>

            <FilterSection filters={filters} onFiltersChange={setFilters} />

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading destinations...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredDestinations.map(destination => (
                  <DestinationCard
                    key={destination.key}
                    destination={destination}
                    onSelect={handleDestinationSelect}
                    selected={selectedDestination?.key === destination.key}
                  />
                ))}
              </div>
            )}

            {selectedDestination && (
              <div className="mt-8 text-center">
                <button
                  onClick={nextStep}
                  className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-lg font-bold rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
                >
                  Continue to Interests →
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Interest Selection */}
        {currentStep === 'interests' && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold text-gray-900">
                ❤️ What interests you in {selectedDestination?.name}?
              </h2>
              <button onClick={prevStep} className="text-gray-500 hover:text-gray-700">
                ← Back
              </button>
            </div>

            {/* Solo Female Traveler Toggle */}
            <div className="mb-6 p-4 bg-pink-50 rounded-lg">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={soloFemaleTraveler}
                  onChange={(e) => {
                    setSoloFemaleTraveler(e.target.checked);
                    if (e.target.checked && !selectedInterests.includes("solo female")) {
                      handleInterestToggle("solo female");
                    }
                  }}
                  className="mr-3 h-5 w-5 text-pink-500"
                />
                <div>
                  <span className="text-lg font-semibold text-gray-900">👩 Solo Female Traveler</span>
                  <p className="text-sm text-gray-600 mt-1">
                    Get safety tips and recommendations specifically for solo female travelers
                  </p>
                </div>
              </label>
            </div>

            {/* Budget Range */}
            <div className="mb-6">
              <label className="block text-lg font-semibold text-gray-700 mb-4">💰 Budget Range</label>
              <div className="grid grid-cols-3 gap-3">
                {['budget', 'mid-range', 'luxury'].map(budget => (
                  <button
                    key={budget}
                    onClick={() => setBudgetRange(budget)}
                    className={`px-4 py-3 rounded-lg border-2 font-semibold capitalize transition-all duration-200 ${
                      budgetRange === budget
                        ? "bg-green-500 border-green-500 text-white shadow-lg"
                        : "bg-white border-gray-300 text-gray-700 hover:border-green-300 hover:bg-green-50"
                    }`}
                  >
                    {budget}
                  </button>
                ))}
              </div>
            </div>

            {/* Interest Selection */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 mb-8">
              {availableInterests.map(interest => (
                <button
                  key={interest}
                  onClick={() => handleInterestToggle(interest)}
                  className={`px-4 py-3 rounded-lg border-2 transition-all duration-200 ${
                    selectedInterests.includes(interest)
                      ? "bg-blue-500 border-blue-500 text-white shadow-lg"
                      : "bg-white border-gray-300 text-gray-700 hover:border-blue-300 hover:bg-blue-50"
                  } ${interest === 'solo female' ? 'border-pink-300 hover:border-pink-400' : ''}`}
                >
                  {interest === 'solo female' ? '👩 ' : ''}
                  {interest}
                </button>
              ))}
            </div>

            {selectedInterests.length > 0 && (
              <div className="text-center">
                <button
                  onClick={nextStep}
                  className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-lg font-bold rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
                >
                  Continue to Dates →
                </button>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Date Selection */}
        {currentStep === 'dates' && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold text-gray-900">📅 When are you traveling?</h2>
              <button onClick={prevStep} className="text-gray-500 hover:text-gray-700">
                ← Back
              </button>
            </div>

            {/* Date Type Toggle */}
            <div className="mb-6">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setUseDates(false)}
                  className={`px-6 py-3 rounded-lg font-semibold ${
                    !useDates
                      ? "bg-blue-500 text-white"
                      : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                  }`}
                >
                  📅 Number of Days
                </button>
                <button
                  onClick={() => setUseDates(true)}
                  className={`px-6 py-3 rounded-lg font-semibold ${
                    useDates
                      ? "bg-blue-500 text-white"
                      : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                  }`}
                >
                  📆 Specific Dates
                </button>
              </div>
            </div>

            {/* Date Input */}
            <div className="mb-8">
              {!useDates ? (
                <div>
                  <label className="block text-lg font-semibold text-gray-700 mb-4">
                    How many days is your trip?
                  </label>
                  <input
                    type="number"
                    value={numberOfDays}
                    onChange={(e) => setNumberOfDays(e.target.value)}
                    placeholder="e.g., 5"
                    min="1"
                    max="14"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              ) : (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <label className="text-lg font-semibold text-gray-700">
                      What are your travel dates?
                    </label>
                    <button
                      onClick={addDate}
                      className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                    >
                      + Add Date
                    </button>
                  </div>
                  <div className="space-y-3">
                    {travelDates.map((date, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <input
                          type="date"
                          value={date}
                          onChange={(e) => handleDateChange(index, e.target.value)}
                          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                        <button
                          onClick={() => removeDate(index)}
                          className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                    {travelDates.length === 0 && (
                      <p className="text-gray-500 text-center py-8">
                        Click "Add Date" to specify your travel dates
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="text-center">
              <button
                onClick={generateItinerary}
                disabled={loading}
                className="px-12 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xl font-bold rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg disabled:opacity-50"
              >
                {loading ? "Creating Your Itinerary..." : "✨ Generate My Itinerary"}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Generated Itinerary */}
        {currentStep === 'itinerary' && itinerary && (
          <div className="space-y-8">
            {/* Itinerary Header */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    🗺️ Your {itinerary.destination} Adventure
                  </h2>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {itinerary.interests.map(interest => (
                      <span
                        key={interest}
                        className={`px-3 py-1 rounded-full text-sm font-medium ${
                          interest === 'solo female' ? 'bg-pink-100 text-pink-800' : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {interest === 'solo female' ? '👩 ' : ''}{interest}
                      </span>
                    ))}
                  </div>
                  {itinerary.solo_female_safety_rating && (
                    <SafetyBadge 
                      rating={itinerary.solo_female_safety_rating} 
                      notes={itinerary.safety_notes} 
                    />
                  )}
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={prevStep}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-semibold"
                  >
                    ← Edit
                  </button>
                  <button
                    onClick={resetApp}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-semibold"
                  >
                    New Trip
                  </button>
                </div>
              </div>
            </div>

            {/* Daily Itineraries */}
            {itinerary.days.map(day => (
              <div key={day.day} className="bg-white rounded-2xl shadow-xl overflow-hidden">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-8 py-6">
                  <h3 className="text-2xl font-bold text-white">
                    Day {day.day} {day.date && `- ${new Date(day.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}`}
                  </h3>
                  <p className="text-blue-100 text-lg mt-2">
                    Estimated Time: {day.total_estimated_time} • {day.activities.length} Activities
                  </p>
                  {day.safety_notes && soloFemaleTraveler && (
                    <div className="mt-3 p-3 bg-blue-400 bg-opacity-30 rounded-lg">
                      <p className="text-blue-100 text-sm">
                        <span className="font-semibold">👩 Solo Female Safety:</span> {day.safety_notes}
                      </p>
                    </div>
                  )}
                </div>

                <div className="p-8">
                  <div className="grid gap-6">
                    {day.activities.map((activity, index) => (
                      <div key={activity.id} className="flex items-start space-x-6 p-6 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-blue-500 text-white rounded-full flex items-center justify-center text-xl font-bold">
                            {index + 1}
                          </div>
                        </div>
                        <div className="flex-grow">
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="text-xl font-bold text-gray-900 mb-2">
                                {activity.name}
                              </h4>
                              <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-3 ${
                                activity.category === 'solo female' ? 'bg-pink-100 text-pink-800' : 'bg-purple-100 text-purple-800'
                              }`}>
                                {activity.category === 'solo female' ? '👩 ' : ''}{activity.category}
                              </span>
                              <p className="text-gray-600 mb-3 leading-relaxed">
                                {activity.description}
                              </p>
                              <div className="space-y-1 text-sm text-gray-500">
                                <p>📍 {activity.address}</p>
                                <p>⏰ Duration: {activity.estimated_duration}</p>
                                <p>🌅 Best Time: {activity.best_time}</p>
                                {activity.solo_female_notes && soloFemaleTraveler && (
                                  <p className="text-pink-600 font-medium">
                                    👩 Solo Female: {activity.solo_female_notes}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}

            {/* Export & Action Buttons */}
            <div className="text-center bg-white rounded-2xl shadow-xl p-8">
              <div className="space-y-4">
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={() => exportItinerary('pdf')}
                    className="px-6 py-3 bg-red-500 text-white text-lg font-bold rounded-xl hover:bg-red-600 transition-all duration-200 shadow-lg"
                  >
                    📄 Export PDF
                  </button>
                  <button
                    onClick={() => exportItinerary('email')}
                    className="px-6 py-3 bg-blue-500 text-white text-lg font-bold rounded-xl hover:bg-blue-600 transition-all duration-200 shadow-lg"
                  >
                    📧 Email Itinerary
                  </button>
                  <button
                    onClick={() => window.print()}
                    className="px-6 py-3 bg-green-500 text-white text-lg font-bold rounded-xl hover:bg-green-600 transition-all duration-200 shadow-lg"
                  >
                    🖨️ Print
                  </button>
                </div>
                <button
                  onClick={resetApp}
                  className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-lg font-bold rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
                >
                  🗺️ Plan Another Adventure
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default EnhancedApp;