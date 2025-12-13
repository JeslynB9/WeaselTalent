document.addEventListener("DOMContentLoaded", () => {
    const locationFilter = document.getElementById("filter-location");
    const skillFilter = document.getElementById("filter-skill");
    const levelFilter = document.getElementById("filter-level");
    const resetBtn = document.getElementById("reset-filters");

    const jobs = document.querySelectorAll(".job-card");

    function applyFilters() {
        const location = locationFilter.value;
        const skill = skillFilter.value;
        const level = levelFilter.value;

        jobs.forEach(job => {
            const jobLocation = job.dataset.location;
            const jobSkill = job.dataset.skill;
            const jobLevel = parseInt(job.dataset.level);

            const locationMatch =
                location === "all" || jobLocation === location;

            const skillMatch =
                skill === "all" || jobSkill === skill;

            const levelMatch =
                level === "all" || jobLevel >= parseInt(level);

            job.style.display =
                locationMatch && skillMatch && levelMatch
                    ? "block"
                    : "none";
        });
    }

    locationFilter.addEventListener("change", applyFilters);
    skillFilter.addEventListener("change", applyFilters);
    levelFilter.addEventListener("change", applyFilters);

    resetBtn.addEventListener("click", () => {
        locationFilter.value = "all";
        skillFilter.value = "all";
        levelFilter.value = "all";
        applyFilters();
    });
});
