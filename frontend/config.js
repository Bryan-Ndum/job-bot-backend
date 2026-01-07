// API Configuration
// This will be set via environment variables in production

const API_BASE_URL = 
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'  // Local development
    : process.env.REACT_APP_API_URL || process.env.NEXT_PUBLIC_API_URL || 'https://your-backend-url.railway.app';  // Production

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { API_BASE_URL };
}






