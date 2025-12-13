// auth page handlers (form submit, call api)
document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll("form");
    forms.forEach(f => {
        f.addEventListener("submit", (e) => {
            e.preventDefault();
            // simple demo behaviour
            alert('Form submitted (demo)');
        });
    });
});
