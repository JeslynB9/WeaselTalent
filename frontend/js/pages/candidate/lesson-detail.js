import { API_BASE } from "../../api-config.module.js";

const CANDIDATE_ID = 1;

const params = new URLSearchParams(window.location.search);
const taskId = params.get("task_id");
const courseId = params.get("course_id");

console.log("Loading task:", taskId);

const titleEl = document.getElementById("lessonTitle");
const bodyEl = document.getElementById("lessonBody");
const completeBtn = document.getElementById("completeLessonBtn");

async function loadLesson() {
  if (!taskId) {
    console.error("No task_id in URL");
    return;
  }

  const res = await fetch(`${API_BASE}/courses/tasks/${taskId}`);
  if (!res.ok) {
    console.error("Failed to fetch lesson");
    return;
  }

  const task = await res.json();
  console.log("Lesson data:", task);

  titleEl.textContent = task.title;
  bodyEl.innerHTML = task.content;
}

completeBtn.onclick = async () => {
  await fetch(`${API_BASE}/courses/tasks/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate_id: CANDIDATE_ID,
      task_id: taskId
    })
  });

  window.location.href =
    `assessment-detail.html?course_id=${courseId}`;
};

loadLesson();
