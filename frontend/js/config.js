// Environment Configuration

// PRODUCTION: Update PRODUCTION_API_URL when deploying (e.g., "https://api.yourleaguename.com")
const PRODUCTION_API_URL = 'http://64.227.184.118:8000';

// DEVELOPMENT: Use localhost for local testing
// For multi-device testing, change to your IP (run: ipconfig | findstr IPv4)
const DEVELOPMENT_API_URL = 'http://64.227.184.118:8000';

// Auto-detect: localhost/127.0.0.1 = development, everything else = production
const isProduction =
    !window.location.hostname.includes('localhost') &&
    !window.location.hostname.includes('127.0.0.1');

const API_BASE_URL = isProduction ? PRODUCTION_API_URL : DEVELOPMENT_API_URL;

// Make available globally
window.API_BASE_URL = API_BASE_URL;

// Helper function to construct API URLs
function getApiUrl(endpoint) {
    // Ensure endpoint starts with /
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${API_BASE_URL}${path}`;
}