document.addEventListener("DOMContentLoaded", () => {
    const mount = document.getElementById("profile-column");

    if (!mount) {
        console.warn("Profile column mount not found");
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
            mount.innerHTML = html;
        })
        .catch(err => console.error(err));
});
