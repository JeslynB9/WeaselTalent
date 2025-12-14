import { API_BASE } from "../../api-config.js";

const CANDIDATE_ID = 1;

const params = new URLSearchParams(window.location.search);
const courseId = params.get("course_id");

const container = document.querySelector(".assessment-path");

// ----------------------------
// Load course + render path
// ----------------------------
async function loadCourse() {
  const res = await fetch(
    `${API_BASE}/courses/${courseId}?candidate_id=${CANDIDATE_ID}`
  );
  const data = await res.json();

  container.innerHTML = `<h2>Assessment</h2>`;

  data.levels
    .sort((a, b) => a.order - b.order)
    .forEach(level => {
      const levelRow = document.createElement("div");
      levelRow.className = "level-row";

      levelRow.innerHTML = `
        <div class="level-title">${level.name}</div>
        <div class="path"></div>
        <div class="status"></div>
      `;

      const path = levelRow.querySelector(".path");

      // ----------------------------
      // Render tasks
      // ----------------------------
      level.tasks
        .sort((a, b) => a.order - b.order)
        .forEach(task => {
          const btn = document.createElement("button");

          // Lesson
          if (task.type === "content") {
            btn.className = "lesson";
            btn.dataset.taskId = task.task_id;
            btn.textContent = "□";

            if (task.completed) {
              btn.classList.add("completed");
            }

            if (!task.unlocked) {
              btn.classList.add("locked");
              btn.disabled = true;
              btn.onclick = null;
            } else {
              btn.onclick = () => {
                window.location.href =
                  `lesson-detail.html?task_id=${task.task_id}&course_id=${courseId}`;
              };
            }
          }

          // Assessment
          if (task.type === "assessment") {
            btn.className = "test";
            btn.textContent = "★";

            if (!task.unlocked) {
              btn.classList.add("locked");
              btn.disabled = true;
              btn.onclick = null;
            } else {
              btn.classList.add("unlocked");
              btn.onclick = () => {
                window.location.href =
                  `assessments-editor.html?task_id=${task.task_id}`;
              };
            }
          }

          path.appendChild(btn);
        });

      // ----------------------------
      // Level status (AFTER tasks)
      // ----------------------------
      const statusEl = levelRow.querySelector(".status");
      const assessmentTask = level.tasks.find(
        t => t.type === "assessment"
      );

      if (assessmentTask?.completed) {
        statusEl.textContent = "Completed";
        statusEl.className = "status completed";
      } 
      else if (!assessmentTask?.unlocked) {
        statusEl.textContent = "Locked";
        statusEl.className = "status locked";
      } 
      else {
        statusEl.textContent = "Available";
        statusEl.className = "status in-progress";
      }

      container.appendChild(levelRow);
    });
}

loadCourse();
