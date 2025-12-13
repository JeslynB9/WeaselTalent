document.addEventListener("DOMContentLoaded", () => {
    const stars = document.querySelectorAll(".star");
    let selectedRating = 0;

    stars.forEach(star => {
        star.addEventListener("click", () => {
            selectedRating = parseInt(star.dataset.value);

            stars.forEach(s => {
                s.classList.toggle(
                    "active",
                    parseInt(s.dataset.value) <= selectedRating
                );
            });
        });
    });
});
