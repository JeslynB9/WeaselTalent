const API_BASE = "http://127.0.0.1:8000";

console.log("login.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");

  if (!form) {
    console.error("loginForm not found");
    return;
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault(); // stops page reload
    login();
  });
});


async function login() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const errorBox = document.getElementById("error");

  console.log("Email:", email);
  console.log("Password:", password);

  errorBox.classList.add("hidden");
  errorBox.textContent = "";

  if (!email || !password) {
    showError("Please enter email and password");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
        showError(typeof data.detail === "string"
        ? data.detail
        : "Login failed");
    return;
    }

    // Success
    localStorage.setItem("user", JSON.stringify(data));

    if (data.role === "recruiter") {
      window.location.href = "../recruiter/dashboard.html";
    } else {
      window.location.href = "../candidate/home.html";
    }

  } catch (err) {
    showError("Cannot connect to server");
  }

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
  }
}