import { useState, useEffect } from "react";
import { fetchPrediction } from "./api/mockPredict.js";

const disasterIcons = {
  Earthquake: "🌎",
  Flood: "🌊",
  Storm: "🌪️",
  Wildfire: "🔥",
  Default: "⚠️",
};

export default function WeatherDisasterApp() {
  const [location, setLocation] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const stored = localStorage.getItem("locationHistory");
    if (stored) setHistory(JSON.parse(stored));
  }, []);

  const saveHistory = (loc) => {
    if (!history.includes(loc)) {
      const updated = [loc, ...history].slice(0, 5);
      setHistory(updated);
      localStorage.setItem("locationHistory", JSON.stringify(updated));
    }
  };

  const fetchData = async (loc = location) => {
    if (!loc.trim()) return;
    setLoading(true);
    setError("");
    setPrediction(null);

    try {
      const predData = await fetchPrediction(loc);
      setPrediction(predData);
      saveHistory(loc);
    } catch (err) {
      setError("Failed to fetch prediction");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case "high":
        return "bg-red-600";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-green-600";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col items-center p-4 text-white">
      <h1 className="text-4xl font-bold mt-6 mb-6">Weather & Disaster Predictor</h1>

      <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md">
        <input
          type="text"
          placeholder="Enter location"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="p-3 rounded text-black flex-1"
        />
        <button
          onClick={() => fetchData()}
          className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700"
        >
          Predict
        </button>
      </div>

      {history.length > 0 && (
        <div className="mt-4 flex gap-2 flex-wrap">
          {history.map((h) => (
            <button
              key={h}
              onClick={() => fetchData(h)}
              className="bg-gray-700 px-3 py-1 rounded hover:bg-gray-600"
            >
              {h}
            </button>
          ))}
        </div>
      )}

      {loading && <p className="mt-4">Loading...</p>}
      {error && <p className="mt-4 text-red-500">{error}</p>}

      {prediction && (
        <div className="mt-6 bg-gray-800 p-4 rounded w-full max-w-md shadow-md">
          <h2 className="text-2xl font-bold mb-4">Disaster Prediction</h2>
          {Object.keys(prediction).map((key) => (
            <div key={key} className="mb-3">
              <div className="flex justify-between items-center mb-1">
                <span className="flex items-center gap-2">
                  {disasterIcons[key] || disasterIcons.Default} <strong>{key}</strong>
                </span>
                <span>{prediction[key]}</span>
              </div>
              <div className="w-full bg-gray-700 h-3 rounded">
                <div
                  className={`${getRiskColor(prediction[key])} h-3 rounded`}
                  style={{ width: prediction[key] === "high" ? "100%" : prediction[key] === "medium" ? "60%" : "30%" }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}