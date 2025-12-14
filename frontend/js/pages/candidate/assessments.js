// assessments.js (ES module)
import { API_BASE } from "../../api-config.module.js";

const CANDIDATE_ID = 1;
const listEl = document.querySelector(".assessment-list");

const levelFilter = document.getElementById("filter-level");
// const domainFilter = document.getElementById("filter-domain");
const statusFilter = document.getElementById("filter-status");
const resetBtn = document.getElementById("reset-filter-btn");

let allCourses = [];


// ----------------------------
// Render 
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

  if (levelFilter.value !== "all") {
    const level = Number(levelFilter.value);
    filtered = filtered.filter(
      c => Number(c.difficulty_level) === level
    );
  }

  if (statusFilter.value === "completed") {
    filtered = filtered.filter(c => c.is_completed);
  } else if (statusFilter.value === "available") {
    filtered = filtered.filter(c => !c.is_completed);
  }

  renderCourses(filtered);
}


// ----------------------------
// Load from backend
// ----------------------------
async function loadCourses() {
  try {
    console.log("loadCourses called");

    const res = await fetch(
      `${API_BASE}/courses?candidate_id=${CANDIDATE_ID}`
    );

    console.log("response status:", res.status);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const courses = await res.json(); // ✅ ONLY ONCE
    console.log("courses from backend:", courses);

    allCourses = courses;
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
// domainFilter.addEventListener("change", applyFilters);
statusFilter.addEventListener("change", applyFilters);

resetBtn.addEventListener("click", () => {
  levelFilter.value = "all";
  // domainFilter.value = "all";
  statusFilter.value = "all";
  renderCourses(allCourses);
});



// ----------------------------
// Init
// ----------------------------
loadCourses();
