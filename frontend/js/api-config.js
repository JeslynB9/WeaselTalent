// ===========================
// API Configuration
// ===========================

const API_BASE = 'http://127.0.0.1:8000'; // backend URL to allow API calls
// default recruiter id for local development; override in pages if needed
const RECRUITER_ID = 1;

// expose globals so non-module scripts can read these values
if (typeof window !== 'undefined') {
	window.API_BASE = API_BASE;
	window.RECRUITER_ID = RECRUITER_ID;
}

console.log("✅ api-config loaded", API_BASE, RECRUITER_ID);