document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('job-create-form');
    const addReqBtn = document.getElementById('add-requirement');
    const requirementsContainer = document.getElementById('requirements');
    const message = document.getElementById('form-message');

    // demo recruiter id (seeded)
    const recruiterId = 10;

    function createRequirementRow() {
        const row = document.createElement('div');
        row.className = 'requirement-row';

        const text = document.createElement('input');
        text.type = 'text';
        text.className = 'req-text';
        text.placeholder = 'Requirement text';
        text.required = true;

        const level = document.createElement('input');
        level.type = 'number';
        level.className = 'req-level';
        level.placeholder = 'Level (1-5)';
        level.min = 1;
        level.max = 5;

        const remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'remove-req';
        remove.textContent = 'Remove';
        remove.addEventListener('click', () => row.remove());

        row.appendChild(text);
        row.appendChild(level);
        row.appendChild(remove);
        return row;
    }

    // wire initial remove buttons
    requirementsContainer.addEventListener('click', (e) => {
        if (e.target && e.target.classList.contains('remove-req')) {
            const row = e.target.closest('.requirement-row');
            if (row) row.remove();
        }
    });

    addReqBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const row = createRequirementRow();
        requirementsContainer.appendChild(row);
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        message.textContent = '';

        const roleIdVal = document.getElementById('role-id').value;
        const companyIdVal = document.getElementById('company-id').value;
        const title = document.getElementById('title').value.trim();
        const description = document.getElementById('description').value.trim();

        if (!companyIdVal || !title) {
            message.textContent = 'Company ID and Title are required.';
            return;
        }

        const requirements = [];
        const rows = requirementsContainer.querySelectorAll('.requirement-row');
        rows.forEach(r => {
            const text = r.querySelector('.req-text')?.value?.trim();
            const level = r.querySelector('.req-level')?.value;
            if (text) {
                requirements.push({ requirement_text: text, level: level ? parseInt(level, 10) : null });
            }
        });

        const payload = {
            company_id: parseInt(companyIdVal, 10),
            title,
            description,
            requirements,
        };
        if (roleIdVal) payload.role_id = parseInt(roleIdVal, 10);

        try {
            const res = await fetch(`${API_BASE}/recruiters/${recruiterId}/roles`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `Status ${res.status}`);
            }

            const data = await res.json();
            message.textContent = `Role created (id=${data.role_id})`;
            form.reset();
            // remove extra requirement rows, keep one
            const currentRows = requirementsContainer.querySelectorAll('.requirement-row');
            currentRows.forEach((r, idx) => { if (idx > 0) r.remove(); });

        } catch (err) {
            console.error('Create role failed', err);
            message.textContent = `Failed to create role: ${err.message}`;
        }
    });
});
