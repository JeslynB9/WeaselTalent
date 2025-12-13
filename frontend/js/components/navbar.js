document.addEventListener("DOMContentLoaded", () => {

    const navLinks = document.querySelectorAll("nav .links a");

    // Highlight active link based on URL
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        const href = link.getAttribute("href");

        if (!href || href === "#") return;

        if (currentPath.includes(href)) {
            link.classList.add("active");
        }
    });

    // Optional: handle "Me" click (profile)
    navLinks.forEach(link => {
        if (link.textContent.trim().toLowerCase() === "me") {
            link.addEventListener("click", (e) => {
                e.preventDefault();
                window.location.href = "../shared/profile.html";
            });
        }
    });

});
