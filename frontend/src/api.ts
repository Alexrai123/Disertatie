import axios from 'axios'

// Configure base URL for API requests
// The frontend expects the backend to be accessible under /api (Nginx reverse proxy or Vite dev proxy)
axios.defaults.baseURL = '/api'

export default axios
