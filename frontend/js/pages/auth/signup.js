import { API_BASE } from "../../api-config.js";

document.getElementById("signupBtn").addEventListener("click", (event) => {
  event.preventDefault(); // Prevent any default form submission
  signup();
});

async function signup() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const role = document.getElementById("role").value;
  const firstName = document.getElementById("firstName").value;
  const lastName = document.getElementById("lastName").value;
  const errorBox = document.getElementById("error");

  errorBox.textContent = ""; // Clear previous messages
  errorBox.style.color = "red"; // Default to error color

  if (!email || !password || !role || !firstName || !lastName) {
    errorBox.textContent = "Please fill in all required fields.";
    return;
  }

  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    errorBox.textContent = "Please enter a valid email address.";
    return;
  }

  console.log("Email:", email);
  console.log("Password:", password);
  console.log("Role:", role);

  try {
    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, role, first_name: firstName, last_name: lastName })
    });

    if (!res.ok) {
      const errorData = await res.json();
      if (errorData.detail && Array.isArray(errorData.detail)) {
        errorBox.textContent = errorData.detail.map(err => err.msg || err.message).join(", ");
      } else {
        errorBox.textContent = errorData.detail || "Signup failed";
      }
    } else {
      // Auto-login after successful signup
      try {
        const loginRes = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password })
        });
        const loginData = await loginRes.json();
        if (loginRes.ok) {
          localStorage.setItem("user_id", loginData.id);
          localStorage.setItem("role", loginData.role);
          errorBox.style.color = "green";
          errorBox.textContent = "Signup successful! Redirecting...";
          setTimeout(() => {
            if (loginData.role === "recruiter") {
              window.location.href = "../recruiter/dashboard.html";
            } else {
              window.location.href = "../candidate/home.html";
            }
          }, 2000);
        } else {
          errorBox.textContent = "Signup successful, but login failed. Please log in manually.";
          setTimeout(() => {
            window.location.href = "login.html";
          }, 2000);
        }
      } catch (loginError) {
        console.error("Auto-login error:", loginError);
        errorBox.textContent = "Signup successful, but login failed. Please log in manually.";
        setTimeout(() => {
          window.location.href = "login.html";
        }, 2000);
      }
    }
  } catch (error) {
    console.error("Signup error:", error);
    errorBox.textContent = "An error occurred. Please try again.";
  }
}