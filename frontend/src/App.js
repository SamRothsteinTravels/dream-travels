import React from "react";
import "./App.css";
import EnhancedApp from "./EnhancedApp";

function App() {
  const [destination, setDestination] = useState("");
  const [selectedInterests, setSelectedInterests] = useState([]);
  const [travelDates, setTravelDates] = useState([]);
  const [numberOfDays, setNumberOfDays] = useState("");
  const [useDates, setUseDates] = useState(false);
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [availableDestinations, setAvailableDestinations] = useState([]);

  useEffect(() => {
    fetchAvailableDestinations();
  }, []);

  const fetchAvailableDestinations = async () => {
    try {
      const response = await axios.get(`${API}/available-destinations`);
      setAvailableDestinations(response.data.destinations);
    } catch (error) {
      console.error("Error fetching destinations:", error);
    }
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

  const generateItinerary = async () => {
    if (!destination || selectedInterests.length === 0) {
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
        destination,
        interests: selectedInterests,
        travel_dates: useDates ? travelDates.filter(date => date) : null,
        number_of_days: useDates ? null : parseInt(numberOfDays)
      };

      const response = await axios.post(`${API}/generate-itinerary`, requestData);
      setItinerary(response.data);
    } catch (error) {
      console.error("Error generating itinerary:", error);
      alert("Error generating itinerary. Please try again!");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setDestination("");
    setSelectedInterests([]);
    setTravelDates([]);
    setNumberOfDays("");
    setItinerary(null);
    setUseDates(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-700">
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-20"
          style={{ backgroundImage: `url(${HERO_IMAGE})` }}
        ></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              Plan Your Perfect Trip
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
              Create personalized itineraries based on your interests, with activities grouped by location for the perfect travel experience.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {!itinerary ? (
          /* Trip Planning Form */
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
              Let's Plan Your Adventure
            </h2>

            {/* Destination Selection */}
            <div className="mb-8">
              <label className="block text-lg font-semibold text-gray-700 mb-4">
                🌍 Where are you going?
              </label>
              <select
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select your destination...</option>
                {availableDestinations.map(dest => (
                  <option key={dest.key} value={dest.name}>
                    {dest.name} - {dest.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Interest Selection */}
            <div className="mb-8">
              <label className="block text-lg font-semibold text-gray-700 mb-4">
                ❤️ What are you interested in?
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {INTEREST_OPTIONS.map(interest => (
                  <button
                    key={interest}
                    onClick={() => handleInterestToggle(interest)}
                    className={`px-4 py-2 rounded-lg border-2 transition-all duration-200 ${
                      selectedInterests.includes(interest)
                        ? "bg-blue-500 border-blue-500 text-white shadow-lg"
                        : "bg-white border-gray-300 text-gray-700 hover:border-blue-300 hover:bg-blue-50"
                    }`}
                  >
                    {interest}
                  </button>
                ))}
              </div>
            </div>

            {/* Date Selection Toggle */}
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

            {/* Date/Duration Input */}
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

            {/* Generate Button */}
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
        ) : (
          /* Generated Itinerary Display */
          <div className="space-y-8">
            {/* Itinerary Header */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    🗺️ Your {itinerary.destination} Itinerary
                  </h2>
                  <div className="flex flex-wrap gap-2">
                    {itinerary.interests.map(interest => (
                      <span
                        key={interest}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                      >
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>
                <button
                  onClick={resetForm}
                  className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-semibold"
                >
                  Plan New Trip
                </button>
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
                              <span className="inline-block px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium mb-3">
                                {activity.category}
                              </span>
                              <p className="text-gray-600 mb-3 leading-relaxed">
                                {activity.description}
                              </p>
                              <div className="space-y-1 text-sm text-gray-500">
                                <p>📍 {activity.address}</p>
                                <p>⏰ Duration: {activity.estimated_duration}</p>
                                <p>🌅 Best Time: {activity.best_time}</p>
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

            {/* Action Buttons */}
            <div className="text-center bg-white rounded-2xl shadow-xl p-8">
              <div className="space-x-4">
                <button
                  onClick={resetForm}
                  className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-lg font-bold rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
                >
                  🗺️ Plan Another Trip
                </button>
                <button
                  onClick={() => window.print()}
                  className="px-8 py-4 bg-green-500 text-white text-lg font-bold rounded-xl hover:bg-green-600 transition-all duration-200 shadow-lg"
                >
                  🖨️ Print Itinerary
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;