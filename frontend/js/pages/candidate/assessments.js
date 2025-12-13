document.addEventListener("DOMContentLoaded", () => {

    const levelFilter = document.getElementById("filter-level");
    const domainFilter = document.getElementById("filter-domain");
    const statusFilter = document.getElementById("filter-status");
    const resetBtn = document.getElementById("reset-filters");

    const assessments = document.querySelectorAll(".assessment");

    // If filters don't exist on this page, exit safely
    if (!levelFilter || !domainFilter || !statusFilter || !resetBtn) {
        return;
    }

    function applyFilters() {
        const level = levelFilter.value;
        const domain = domainFilter.value;
        const status = statusFilter.value;

        assessments.forEach(card => {
            const cardLevel = card.dataset.level;
            const cardDomain = card.dataset.domain;
            const cardStatus = card.dataset.status;

            const levelMatch = level === "all" || cardLevel === level;
            const domainMatch = domain === "all" || cardDomain === domain;
            const statusMatch = status === "all" || cardStatus === status;

            card.style.display =
                levelMatch && domainMatch && statusMatch
                    ? "block"
                    : "none";
        });
    }

    levelFilter.addEventListener("change", applyFilters);
    domainFilter.addEventListener("change", applyFilters);
    statusFilter.addEventListener("change", applyFilters);

    resetBtn.addEventListener("click", () => {
        levelFilter.value = "all";
        domainFilter.value = "all";
        statusFilter.value = "all";
        applyFilters();
    });

});
