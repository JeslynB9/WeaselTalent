// ===========================
// MOCK DATA (frontend only)
// ===========================

const JOBS = [
  {
    id: "job_1",
    title: "Backend Intern (Node.js)",
    requirements: ["Node.js", "APIs", "SQL", "Git"]
  },
  {
    id: "job_2",
    title: "C++ Backend Engineer (Junior)",
    requirements: ["C++", "Data Structures", "APIs", "Performance"]
  },
  {
    id: "job_3",
    title: "Data / Platform Intern",
    requirements: ["SQL", "Python", "ETL", "APIs"]
  }
];

// Candidates are anonymous
const CANDIDATES = [
  {
    id: "CND-1048",
    lastActive: "2025-12-13T08:52:00+11:00",
    skills: ["Node.js", "APIs", "SQL", "Express"],
    domains: ["Node.js", "APIs", "SQL"],
    assessments: [
      { domain: "Node.js", level: 2, score: 7, total: 10 },
      { domain: "APIs", level: 2, score: 8, total: 10 },
      { domain: "SQL", level: 1, score: 6, total: 10 }
    ]
  },
  {
    id: "CND-2091",
    lastActive: "2025-12-12T20:12:00+11:00",
    skills: ["C++", "STL", "Memory", "Networking"],
    domains: ["C++ Backend", "APIs"],
    assessments: [
      { domain: "C++ Backend", level: 3, score: 9, total: 10 },
      { domain: "APIs", level: 1, score: 5, total: 10 }
    ]
  },
  {
    id: "CND-3307",
    lastActive: "2025-12-10T18:05:00+11:00",
    skills: ["SQL", "Python", "Pandas", "ETL"],
    domains: ["SQL", "APIs"],
    assessments: [
      { domain: "SQL", level: 3, score: 8, total: 10 },
      { domain: "APIs", level: 2, score: 7, total: 10 }
    ]
  },
  {
    id: "CND-7780",
    lastActive: "2025-12-13T09:40:00+11:00",
    skills: ["Node.js", "React", "MongoDB"],
    domains: ["Node.js"],
    assessments: [
      { domain: "Node.js", level: 1, score: 5, total: 10 }
    ]
  }
];

// Availability slots (local demo state)
let availability = [
  { id: "slot_1", day: "Tue", start: "10:00", end: "12:00" },
  { id: "slot_2", day: "Thu", start: "14:00", end: "16:00" }
];

// Notes store (local demo state)
const NOTES = {};

// Bookings store (local demo state)
const BOOKINGS = [];
