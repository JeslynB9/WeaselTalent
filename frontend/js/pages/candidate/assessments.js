// assessments.js (ES module)

import { API_BASE } from "../../api-config.js";

const CANDIDATE_ID = 1;
const listEl = document.querySelector(".assessment-list");

async function loadCourses() {
  try {
    const res = await fetch(
      `${API_BASE}/courses?candidate_id=${CANDIDATE_ID}`
    );

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const courses = await res.json();
    listEl.innerHTML = "";

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

  } catch (err) {
    console.error("Failed to load courses:", err);
    listEl.innerHTML =
      "<p class='error'>Could not load courses.</p>";
  }
}

loadCourses();
