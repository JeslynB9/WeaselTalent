document.addEventListener("DOMContentLoaded", () => {
    const mount = document.getElementById("profile-column");
    const user = JSON.parse(localStorage.getItem("user"));

    if (!mount) {
        console.warn("Profile column mount not found");
        return;
    }

    if (!user) {
        window.location.href = "../auth/login.html";
        return;
    }

    fetch("../../pages/shared/profile-column.html")
        .then(res => {
            if (!res.ok) {
                throw new Error("Failed to load profile column");
            }
            return res.text();
        })
        .then(html => {
            // Inject HTML
            mount.innerHTML = html;

            // Element exists
            const nameEl = mount.querySelector("#user-name");
            if (nameEl) {
                nameEl.textContent = user.full_name || user.email;
            } else {
                console.warn("#user-name not found in profile column");
            }
        })
        .catch(err => console.error(err));
});
