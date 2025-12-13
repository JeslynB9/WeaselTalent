document.addEventListener("DOMContentLoaded", () => {

    const roleFilter = document.getElementById("filter-role");
    const matchFilter = document.getElementById("filter-match");
    const resetBtn = document.getElementById("reset-filters");

    const cards = document.querySelectorAll(".candidate-card");

    if (!roleFilter || !matchFilter || !resetBtn) return;

    function applyFilters() {
        const role = roleFilter.value;
        const match = matchFilter.value;

        cards.forEach(card => {
            const cardRole = card.dataset.role;
            const cardMatch = parseInt(card.dataset.match);

            const roleMatch = role === "all" || cardRole === role;
            const matchMatch = match === "all" || cardMatch >= parseInt(match);

            card.style.display =
                roleMatch && matchMatch ? "block" : "none";
        });
    }

    roleFilter.addEventListener("change", applyFilters);
    matchFilter.addEventListener("change", applyFilters);

    resetBtn.addEventListener("click", () => {
        roleFilter.value = "all";
        matchFilter.value = "all";
        applyFilters();
    });

});
