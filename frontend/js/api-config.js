// ===========================
// API Configuration (global script)
// This file is intended to be included with a plain <script> tag and will
// expose globals `API_BASE` and `RECRUITER_ID` on window.
// For module usage import from `api-config.module.js` instead.
// ===========================

const API_BASE = 'http://127.0.0.1:8000'; // backend URL to allow API calls
const RECRUITER_ID = 10;

if (typeof window !== 'undefined') {
	window.API_BASE = API_BASE;
	window.RECRUITER_ID = RECRUITER_ID;
}