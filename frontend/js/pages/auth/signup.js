// simple checker to check if js is connected
console.log("signup.js loaded");

const API_BASE = "http://127.0.0.1:8000";

document.getElementById("signupBtn").addEventListener("click", (event) => {
  event.preventDefault();
  signup();
});

async function signup() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const role = document.getElementById("role").value;
  const firstName = document.getElementById("firstName").value;
  const lastName = document.getElementById("lastName").value;
  const errorBox = document.getElementById("error");

  errorBox.textContent = "";
  errorBox.style.color = "red";

  if (!email || !password || !role || !firstName || !lastName) {
    errorBox.textContent = "Please fill in all required fields.";
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    errorBox.textContent = "Please enter a valid email address.";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
            email, 
            password, 
            role,
            first_name: firstName,
            last_name: lastName
        })
    });

    if (!res.ok) {
      const errorData = await res.json();
      errorBox.textContent = errorData.detail || "Signup failed";
      return;
    }

    const user = await res.json();
    // store entire user object
    localStorage.setItem("user", JSON.stringify(user));

    errorBox.style.color = "green";
    errorBox.textContent = "Signup successful! Redirecting...";

    setTimeout(() => {
      if (user.role === "recruiter") {
        window.location.href = "../recruiter/dashboard.html";
      } else {
        window.location.href = "../candidate/home.html";
      }
    }, 800);

  } catch (error) {
    console.error("Signup error:", error);
    errorBox.textContent = "An error occurred. Please try again.";
  }
}
