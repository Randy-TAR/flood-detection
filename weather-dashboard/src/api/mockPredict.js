export const fetchPrediction = async (location) => {
  await new Promise((res) => setTimeout(res, 500));
  return {
    Earthquake: ["low", "medium", "high"][Math.floor(Math.random() * 3)],
    Flood: ["low", "medium", "high"][Math.floor(Math.random() * 3)],
    Storm: ["low", "medium", "high"][Math.floor(Math.random() * 3)],
    Wildfire: ["low", "medium", "high"][Math.floor(Math.random() * 3)]
  };
};