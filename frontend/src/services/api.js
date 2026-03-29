const BASE_URL = "http://127.0.0.1:8000";

export const searchQuery = async (q) => {
  const res = await fetch(`${BASE_URL}/search?q=${q}`);
  return res.json();
};

export const getTrends = async () => {
  const res = await fetch("http://127.0.0.1:8000/trends");
  return res.json();
};

export const getRegionTrends = async (state) => {
  const res = await fetch(`http://127.0.0.1:8000/region?state=${state}`);
  return res.json();
};