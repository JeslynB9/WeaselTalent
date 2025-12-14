document.addEventListener("DOMContentLoaded", () => {
    const locationFilter = document.getElementById("filter-location");
    const skillFilter = document.getElementById("filter-skill");
    const levelFilter = document.getElementById("filter-level");
    const resetBtn = document.getElementById("reset-job-filters");
    const jobsList = document.getElementById("jobs-list");

    if (!jobsList) {
        console.warn("jobs-list mount not found");
        return;
    }

    async function loadJobs() {
        jobsList.innerHTML = '<div class="muted">Loading jobs...</div>';

        const apiBase = (typeof window !== 'undefined' && window.API_BASE) ? window.API_BASE : (typeof API_BASE !== 'undefined' ? API_BASE : '');
        const recruiterId = (typeof window !== 'undefined' && window.RECRUITER_ID) ? window.RECRUITER_ID : (typeof RECRUITER_ID !== 'undefined' ? RECRUITER_ID : 0);

        if (!apiBase || !recruiterId) {
            jobsList.innerHTML = '<div class="muted">API configuration missing</div>';
            return;
        }

        try {
            const res = await fetch(`${apiBase}/recruiters/${recruiterId}/roles`);
            if (!res.ok) throw new Error(`Status ${res.status}`);
            const data = await res.json();

            if (!data || !data.length) {
                jobsList.innerHTML = '<div class="muted">No jobs found.</div>';
                return;
            }

            jobsList.innerHTML = data.map(renderJobCard).join('\n');
            applyFilters();
        } catch (err) {
            console.error('Failed to load jobs', err);
            jobsList.innerHTML = `<div class="muted">Error loading jobs: ${err.message}</div>`;
        }
    }

    function escapeHtml(s) {
        return (s || '').toString().replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function renderJobCard(r) {
        // company name isn't returned from the simple endpoint; show company_id as placeholder
        const company = r.company_id ? `Company ${r.company_id}` : '';

        // derive primary skill and level from free-text requirements if available
        let skill = 'all';
        let level = 2;
        if (r.requirements && r.requirements.length) {
            const first = r.requirements[0];
            const txt = (first.text || first.requirement_text || '').toLowerCase();
            if (txt.includes('python')) skill = 'python';
            else if (txt.includes('backend')) skill = 'backend';
            else if (txt.includes('frontend')) skill = 'frontend';
            if (first.level) level = first.level;
        }

        const tagsHtml = (r.requirements || []).slice(0, 4).map(q => `<span class="tag">${escapeHtml(q.text || q.requirement_text || '')}</span>`).join(' ');

        return `
            <div class="job-card" data-location="remote" data-skill="${skill}" data-level="${level}">
                <div class="job-header">
                    <div>
                        <h4>${escapeHtml(r.title)}</h4>
                        <p class="company">${escapeHtml(company)}</p>
                    </div>
                </div>

                <div class="job-meta">🌍 Remote · ${escapeHtml(r.description || '')}</div>

                <div class="tags">${tagsHtml}</div>

                <div class="actions">
                    <button class="secondary">View Details</button>
                    <button class="primary" onclick="window.location.href='../../pages/recruiter/job-candidates.html'">View Candidates</button>
                </div>
            </div>
        `;
    }

    function applyFilters() {
        const location = locationFilter.value;
        const skill = skillFilter.value;
        const level = levelFilter.value;

        const jobs = document.querySelectorAll('.job-card');
        jobs.forEach(job => {
            const jobLocation = job.dataset.location || '';
            const jobSkill = job.dataset.skill || 'all';
            const jobLevel = parseInt(job.dataset.level || '0');

            const locationMatch = location === 'all' || jobLocation === location;
            const skillMatch = skill === 'all' || jobSkill === skill;
            const levelMatch = level === 'all' || jobLevel >= parseInt(level);

            job.style.display = (locationMatch && skillMatch && levelMatch) ? 'block' : 'none';
        });
    }

    locationFilter.addEventListener('change', applyFilters);
    skillFilter.addEventListener('change', applyFilters);
    levelFilter.addEventListener('change', applyFilters);

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            locationFilter.value = 'all';
            skillFilter.value = 'all';
            levelFilter.value = 'all';
            applyFilters();
        });
    }

    // initial load
    loadJobs();
});
