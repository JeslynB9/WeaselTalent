// ES module variant of API config. Exports constants for module imports
export const API_BASE = 'http://127.0.0.1:8000';
export const RECRUITER_ID = 1;

// Also make available as globals so non-module scripts can read them
if (typeof window !== 'undefined') {
    window.API_BASE = API_BASE;
    window.RECRUITER_ID = RECRUITER_ID;
}
