document.addEventListener("DOMContentLoaded", () => {

    const locationFilter = document.getElementById("filter-location");
    const skillFilter = document.getElementById("filter-skill");
    const matchFilter = document.getElementById("filter-match");
    const resetBtn = document.getElementById("reset-job-filters");

    const jobs = document.querySelectorAll(".job-card");

    if (!locationFilter || !skillFilter || !matchFilter || !resetBtn) return;

    function applyFilters() {
        const location = locationFilter.value;
        const skill = skillFilter.value;
        const match = matchFilter.value;

        jobs.forEach(job => {
            const jobLocation = job.dataset.location;
            const jobSkill = job.dataset.skill;
            const jobMatch = parseInt(job.dataset.match);

            const locationMatch =
                location === "all" || jobLocation === location;

            const skillMatch =
                skill === "all" || jobSkill === skill;

            const matchMatch =
                match === "all" || jobMatch >= parseInt(match);

            job.style.display =
                locationMatch && skillMatch && matchMatch
                    ? "block"
                    : "none";
        });
    }

    locationFilter.addEventListener("change", applyFilters);
    skillFilter.addEventListener("change", applyFilters);
    matchFilter.addEventListener("change", applyFilters);

    resetBtn.addEventListener("click", () => {
        locationFilter.value = "all";
        skillFilter.value = "all";
        matchFilter.value = "all";
        applyFilters();
    });

});
