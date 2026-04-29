import axios from "axios";

const API = axios.create({
  baseURL: "https://fintech-payout-engine.onrender.com/api",
});

export default API;