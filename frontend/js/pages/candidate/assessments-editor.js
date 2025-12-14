import { API_BASE } from "../../api-config.js";

document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const taskId = urlParams.get("task_id");

    if (!taskId) {
        alert("No task selected");
        window.location.href = "assessments.html";
        return;
    }

    // For now, since we don't have a way to get task by id, assume we have the content from detail
    // In a real app, fetch task details
    // For demo, set some content
    document.querySelector(".card-header h3").textContent = "Assessment Task";
    document.querySelector("h4").textContent = "Task Title";
    document.querySelector("p").textContent = "Task content here...";

    // Initialize CodeMirror
    const editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
        lineNumbers: true,
        mode: "python",
        theme: "material"
    });

    const runBtn = document.getElementById("run-btn");
    const submitBtn = document.getElementById("submit-btn");
    const output = document.getElementById("output");

    let pyodideReady = false;
    let pyodide;

    // Load Pyodide
    async function loadPyodideAndSetup() {
        output.textContent = "Loading Python environment...";
        pyodide = await loadPyodide();

        await pyodide.runPythonAsync(`
import sys
from js import console

class OutputCatcher:
    def __init__(self):
        self.text = ""
    def write(self, s):
        self.text += s
    def flush(self):
        pass

sys.stdout = OutputCatcher()
sys.stderr = OutputCatcher()
`);

        pyodideReady = true;
        runBtn.disabled = false;
        submitBtn.disabled = false;
        output.textContent = "Python environment ready!\n";
    }

    loadPyodideAndSetup();

    // Run code
    runBtn.addEventListener("click", async () => {
        if (!pyodideReady) {
            output.textContent = "Python environment still loading...";
            return;
        }

        const code = editor.getValue();
        output.textContent = "";

        try {
            const result = await pyodide.runPythonAsync(code);
            const printed = await pyodide.runPythonAsync("sys.stdout.text");
            output.textContent = printed;
            if (result !== undefined) output.textContent += "\n" + result;
            await pyodide.runPythonAsync("sys.stdout.text = ''");
        } catch (err) {
            output.textContent += err;
        }
    });

    // Submit code
    submitBtn.addEventListener("click", async () => {
        const code = editor.getValue();
        const userId = localStorage.getItem("user_id");

        try {
            const response = await fetch(`${API_BASE}/assessments/submit`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ candidate_id: parseInt(userId), task_id: parseInt(taskId), answer_text: code })
            });

            const result = await response.json();
            if (response.ok) {
                alert("Submitted successfully! Score: " + (result.score || "N/A"));
                window.location.href = "assessments.html";
            } else {
                alert("Submission failed: " + result.detail);
            }
        } catch (error) {
            console.error("Submit error:", error);
            alert("Error submitting. Please try again.");
        }
    });
});