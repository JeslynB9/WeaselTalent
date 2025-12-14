document.addEventListener("DOMContentLoaded", () => {
    const resultFilter = document.getElementById("filter-result");
    const typeFilter = document.getElementById("filter-type");
    const resetBtn = document.getElementById("reset-interview-filters");
    const listContainer = document.querySelector('.interview-list');

    // get candidate id from localStorage (set at login) or query param
    const params = new URLSearchParams(window.location.search);
    const candidateId = params.get('candidate_id') || localStorage.getItem('user_id');

    function renderInterviews(items) {
        if (!listContainer) return;
        if (!items || !items.length) {
            listContainer.innerHTML = '<div class="muted">No interviews yet.</div>';
            return;
        }

        listContainer.innerHTML = items.map(i => `
            <div class="interview-card" data-result="${i.status || ''}" data-type="${i.role_title || ''}">
                <div class="interview-header">
                    <div>
                        <h4>${i.role_title || 'Interview'}</h4>
                        <p class="company">${i.role_title ? i.role_title : ''}</p>
                        <p class="meta">Status: ${i.status || ''}</p>
                    </div>
                    <span class="result ${i.has_notes ? 'passed' : 'muted'}">${i.has_notes ? 'Feedback' : 'No Feedback'}</span>
                </div>
                <div class="actions">
                    <button class="secondary view-feedback" onclick="window.location.href='../../pages/candidate/interview-feedback.html?interview_id=${i.interview_id}'">View Feedback</button>
                </div>
            </div>
        `).join('');

        // Re-bind filters
        applyFilters();
    }

    async function loadInterviews() {
        if (!candidateId) {
            if (listContainer) listContainer.innerHTML = '<div class="muted">Please log in to see interviews.</div>';
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/interviews/candidates/${candidateId}`);
            if (!res.ok) throw new Error('Failed to load interviews');
            const data = await res.json();
            renderInterviews(data);
        } catch (err) {
            console.error('Failed to fetch interviews', err);
            if (listContainer) listContainer.innerHTML = '<div class="muted">Error loading interviews.</div>';
        }
    }

    function applyFilters() {
        const result = resultFilter.value;
        const type = typeFilter.value;

        const cards = document.querySelectorAll('.interview-card');
        cards.forEach(card => {
            const cardResult = card.dataset.result;
            const cardType = card.dataset.type;

            const resultMatch = result === 'all' || cardResult === result;
            const typeMatch = type === 'all' || cardType.toLowerCase().includes(type.toLowerCase());

            card.style.display = (resultMatch && typeMatch) ? 'block' : 'none';
        });
    }

    resultFilter.addEventListener('change', applyFilters);
    typeFilter.addEventListener('change', applyFilters);

    resetBtn.addEventListener('click', () => {
        resultFilter.value = 'all';
        typeFilter.value = 'all';
        applyFilters();
    });

    // initial load
    loadInterviews();

});
