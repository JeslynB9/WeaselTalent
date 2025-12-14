console.log("home.js loaded for user:");

document.addEventListener("DOMContentLoaded", () => {
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user) {
        // not logged in, then go back to login
        window.location.href = "../auth/login.html";
        return;
    }
    console.log("Logged in user:", user);

    const nameEl = document.getElementById("user-name");
    if (nameEl) {
        nameEl.textContent = user.full_name || user.email;
    }
})
