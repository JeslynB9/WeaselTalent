document.addEventListener("DOMContentLoaded", () => {

    const resultFilter = document.getElementById("filter-result");
    const typeFilter = document.getElementById("filter-type");
    const resetBtn = document.getElementById("reset-interview-filters");

    const interviews = document.querySelectorAll(".interview-card");

    // Defensive: exit if filters not on page
    if (!resultFilter || !typeFilter || !resetBtn) return;

    function applyFilters() {
        const result = resultFilter.value;
        const type = typeFilter.value;

        interviews.forEach(card => {
            const cardResult = card.dataset.result;
            const cardType = card.dataset.type;

            const resultMatch =
                result === "all" || cardResult === result;

            const typeMatch =
                type === "all" || cardType === type;

            card.style.display =
                resultMatch && typeMatch
                    ? "block"
                    : "none";
        });
    }

    resultFilter.addEventListener("change", applyFilters);
    typeFilter.addEventListener("change", applyFilters);

    resetBtn.addEventListener("click", () => {
        resultFilter.value = "all";
        typeFilter.value = "all";
        applyFilters();
    });

});
