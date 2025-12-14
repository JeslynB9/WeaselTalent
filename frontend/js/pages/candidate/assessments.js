// assessments.js (ES module)
import { API_BASE } from "../../api-config.js";

const CANDIDATE_ID = 1;
const listEl = document.querySelector(".assessment-list");

const levelFilter = document.getElementById("filter-level");
const domainFilter = document.getElementById("filter-domain");
const statusFilter = document.getElementById("filter-status");
const resetBtn = document.getElementById("reset-filter-btn");

let allCourses = [];

// ----------------------------
// Render (KEEP ORIGINAL STYLING)
// ----------------------------
function renderCourses(courses) {
  listEl.innerHTML = "";

  if (courses.length === 0) {
    listEl.innerHTML =
      "<p class='empty'>No assessments match your filters.</p>";
    return;
  }

  courses.forEach(course => {
    const card = document.createElement("div");
    card.className = `assessment ${
      course.is_completed ? "completed" : "available"
    }`;

    card.innerHTML = `
      <div class="assessment-header">
        <span class="level level-${course.difficulty_level}">
          Level ${course.difficulty_level}
        </span>
        ${
          course.is_completed
            ? `<span class="status completed">✔ Completed</span>`
            : ""
        }
      </div>

      <h4>${course.description}</h4>
      <p>⏱ ${course.time_limit_minutes} minutes</p>

      ${
        course.is_completed
          ? `<p class="score">🏆 Score: ${course.score}%</p>`
          : `<button class="start">Start</button>`
      }
    `;

    if (!course.is_completed) {
      card.querySelector(".start").onclick = () => {
        window.location.href =
          `assessment-detail.html?course_id=${course.course_id}`;
      };
    }

    listEl.appendChild(card);
  });
}

// ----------------------------
// Apply filters
// ----------------------------
function applyFilters() {
  let filtered = [...allCourses];

  // Level
  if (levelFilter.value !== "all") {
    filtered = filtered.filter(
      c => c.difficulty_level === Number(levelFilter.value)
    );
  }

  // Status
  if (statusFilter.value === "completed") {
    filtered = filtered.filter(c => c.is_completed);
  } else if (statusFilter.value === "available") {
    filtered = filtered.filter(c => !c.is_completed);
  } else if (statusFilter.value === "locked") {
    filtered = []; // placeholder (no locked data yet)
  }

  // Domain (future-proof)
  if (domainFilter.value !== "all") {
    filtered = filtered.filter(
      c => c.domain === domainFilter.value
    );
  }

  renderCourses(filtered);
}

// ----------------------------
// Load from backend
// ----------------------------
async function loadCourses() {
  try {
    const res = await fetch(
      `${API_BASE}/courses?candidate_id=${CANDIDATE_ID}`
    );

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    allCourses = await res.json();
    renderCourses(allCourses);

  } catch (err) {
    console.error("Failed to load courses:", err);
    listEl.innerHTML =
      "<p class='error'>Could not load courses.</p>";
  }
}

// ----------------------------
// Events
// ----------------------------
levelFilter.addEventListener("change", applyFilters);
domainFilter.addEventListener("change", applyFilters);
statusFilter.addEventListener("change", applyFilters);

resetBtn.addEventListener("click", () => {
  levelFilter.value = "all";
  domainFilter.value = "all";
  statusFilter.value = "all";
  renderCourses(allCourses);
});

// ----------------------------
// Init
// ----------------------------
loadCourses();
