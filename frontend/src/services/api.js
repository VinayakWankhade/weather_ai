import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 90000, // 90 seconds timeout for production/cold starts
  headers: {
    "Content-Type": "application/json",
  },
});

export const sendMessage = async (message) => {
  try {
    const response = await api.post("/chat", { message });
    return response.data.response;
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
};

export default api;
