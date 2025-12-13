document.addEventListener("DOMContentLoaded", () => {
    const mount = document.getElementById("recruiter-column");

    if (!mount) {
        console.warn("Recruiter column mount not found");
        return;
    }

    fetch("../../pages/shared/recruiter-column.html")
        .then(res => {
            if (!res.ok) {
                throw new Error("Failed to load recruiter column");
            }
            return res.text();
        })
        .then(html => {
            mount.innerHTML = html;
        })
        .catch(err => console.error(err));
});
