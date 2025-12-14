document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const candidateId = params.get('candidate_id');
    const role = params.get('role');
    // role param may be either a role_id (numeric) or a role slug/title (e.g. 'backend')
    const saveBtn = document.getElementById('saveFeedbackBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const status = document.getElementById('saveStatus');
    const roleSelect = document.getElementById('roleSelect');

    function showStatus(msg, ok = true) {
        status.textContent = msg;
        status.style.color = ok ? 'green' : 'red';
    }

    // Draft persistence to avoid losing input on accidental reload/navigation
    const draftKey = `feedback_draft:${candidateId}:${role || ''}`;
    const savedKey = `feedback_saved:${candidateId}:${role || ''}`;
    function saveDraft(notes, fit_score) {
        try {
            const payload = { notes: notes || '', fit_score: fit_score || null, updated: Date.now() };
            localStorage.setItem(draftKey, JSON.stringify(payload));
        } catch (e) { console.warn('Failed to save draft', e); }
    }

    function loadDraft() {
        try {
            const raw = localStorage.getItem(draftKey);
            if (!raw) return null;
            return JSON.parse(raw);
        } catch (e) { return null; }
    }

    function saveSavedRecord(notes, fit_score, interviewId, role_id, role_title) {
        try {
            const payload = { notes: notes || '', fit_score: fit_score || null, interviewId: interviewId || null, role_id: role_id || null, role_title: role_title || null, savedAt: Date.now() };
            localStorage.setItem(savedKey, JSON.stringify(payload));
        } catch (e) { console.warn('Failed to save saved-record', e); }
    }

    function loadSavedRecord() {
        try {
            const raw = localStorage.getItem(savedKey);
            if (!raw) return null;
            return JSON.parse(raw);
        } catch (e) { return null; }
    }

    if (!candidateId) {
        showStatus('No candidate specified', false);
        saveBtn.disabled = true;
        return;
    }

    // Load roles on page load so the user can pick a role if the query param is non-numeric
    async function loadRoles() {
        if (!roleSelect) return;
        roleSelect.innerHTML = '<option value="">Loading roles...</option>';
        try {
            const res = await fetch(`${API_BASE}/recruiters/${RECRUITER_ID}/roles`);
            if (!res.ok) throw new Error('Failed to load roles');
            const roles = await res.json();
            if (!roles || !roles.length) {
                roleSelect.innerHTML = '<option value="">No roles available</option>';
                return;
            }
            roleSelect.innerHTML = '<option value="">Select a role</option>' + roles.map(r => `\n                <option value="${r.role_id}">${r.title}</option>`).join('');

            // Try to preselect based on role query param (slug or id)
            if (role) {
                // if numeric, set directly
                if (/^\d+$/.test(role)) {
                    roleSelect.value = role;
                } else {
                    const lower = role.toLowerCase();
                    const match = roles.find(r => (r.title && r.title.toLowerCase() === lower) || (r.title && r.title.toLowerCase().includes(lower)) || String(r.role_id) === role);
                    if (match) roleSelect.value = match.role_id;
                }
            }
        } catch (e) {
            console.warn('Failed to load roles', e);
            roleSelect.innerHTML = '<option value="">Error loading roles</option>';
        }
    }

    loadRoles();

    // Restore draft if present
    const existingDraft = loadDraft();
    if (existingDraft) {
        try {
            if (existingDraft.notes) {
                // split notes into positives/negatives if our storage has them combined
                const parts = existingDraft.notes.split('\n\n');
                document.getElementById('positives').value = parts[0] || '';
                document.getElementById('negatives').value = parts[1] || '';
            }
            if (existingDraft.fit_score) setRating(existingDraft.fit_score);
            showStatus('Restored draft — your inputs were preserved');
        } catch (e) { console.warn('Failed to restore draft', e); }
    }

    // Restore saved preview if present
    const existingSaved = loadSavedRecord();
    if (existingSaved) {
        try {
            let preview = document.getElementById('savedPreview');
            if (!preview) {
                preview = document.createElement('div');
                preview.id = 'savedPreview';
                preview.style.marginTop = '8px';
                preview.className = 'card muted';
                status.insertAdjacentElement('afterend', preview);
            }
            // build stars
            const stars = (n) => {
                const filled = '★'.repeat(Math.max(0, Math.min(5, n || 0)));
                const empty = '☆'.repeat(5 - Math.max(0, Math.min(5, n || 0)));
                return `<span style="color:#f5b400">${filled}</span><span style="color:#ccc">${empty}</span>`;
            };
            const roleLabel = existingSaved.role_title ? `<div><strong>Role:</strong> ${existingSaved.role_title}</div>` : '';
            const scoreLabel = existingSaved.fit_score ? `<div style="margin-top:6px"><strong>Rating:</strong> ${stars(existingSaved.fit_score)}</div>` : '';
            // split notes into positives / negatives by double newline
            const parts = (existingSaved.notes || '').split('\n\n');
            const positives = parts[0] || '';
            const negatives = parts.slice(1).join('\n\n') || '';
            const positivesHtml = `<div style="margin-top:8px"><strong>Positives:</strong><div style="white-space:pre-wrap;margin-top:4px">${positives}</div></div>`;
            const negativesHtml = `<div style="margin-top:8px"><strong>Negatives:</strong><div style="white-space:pre-wrap;margin-top:4px">${negatives}</div></div>`;
            preview.innerHTML = `<strong>Last saved feedback:</strong>${roleLabel}${scoreLabel}${positivesHtml}${negativesHtml}`;
        } catch (e) { console.warn('Failed to restore saved preview', e); }
    }

    cancelBtn.addEventListener('click', () => {
        window.location.href = '../../pages/recruiter/interviews.html';
    });

    // rating stars handling
    const starButtons = Array.from(document.querySelectorAll('#rating .star'));
    function setRating(n) {
        starButtons.forEach(s => {
            const v = parseInt(s.dataset.value, 10);
            if (v <= n) {
                s.classList.add('filled');
                s.setAttribute('aria-checked', 'true');
            } else {
                s.classList.remove('filled');
                s.setAttribute('aria-checked', 'false');
            }
        });
    }
    starButtons.forEach(s => s.addEventListener('click', () => setRating(parseInt(s.dataset.value, 10))));

    // Save draft on changes
    const positivesEl = document.getElementById('positives');
    const negativesEl = document.getElementById('negatives');
    function persistCurrentDraft() {
        const notesVal = (positivesEl.value || '').trim() + ((positivesEl.value && negativesEl.value) ? '\n\n' : '') + (negativesEl.value || '').trim();
        const currentRating = (function() {
            const sel = starButtons.find(s => s.classList.contains('filled'));
            if (!sel) return null;
            return Math.max(...starButtons.filter(s=>s.classList.contains('filled')).map(s=>parseInt(s.dataset.value,10)));
        })();
        saveDraft(notesVal, currentRating);
    }

    positivesEl.addEventListener('input', persistCurrentDraft);
    negativesEl.addEventListener('input', persistCurrentDraft);
    starButtons.forEach(s => s.addEventListener('click', persistCurrentDraft));

    saveBtn.addEventListener('click', async () => {
        const positives = document.getElementById('positives').value.trim();
        const negatives = document.getElementById('negatives').value.trim();
        const rating = (function() {
            const sel = starButtons.find(s => s.classList.contains('filled'));
            if (!sel) return null;
            // highest filled value
            return Math.max(...starButtons.filter(s=>s.classList.contains('filled')).map(s=>parseInt(s.dataset.value,10)));
        })();

        if (!positives && !negatives) {
            showStatus('Please add positives or negatives', false);
            return;
        }

        // Combine into a single notes field separated by a blank line, so candidate view can split
        const notes = positives + (positives && negatives ? '\n\n' : '') + negatives;

    // disable save to prevent duplicate requests / accidental navigation
    saveBtn.disabled = true;
    try {
            // Normalize role -> role_id. If role is numeric use it, otherwise attempt to lookup by title/slug
            let roleId = null;
            if (role) {
                if (/^\d+$/.test(role)) {
                    roleId = parseInt(role, 10);
                } else {
                    // fetch roles for recruiter and try to match by title or simple slug
                    try {
                        const rolesRes = await fetch(`${API_BASE}/recruiters/${RECRUITER_ID}/roles`);
                        if (rolesRes.ok) {
                            const roles = await rolesRes.json();
                            const lower = role.toLowerCase();
                            const found = roles.find(r => (r.title && r.title.toLowerCase() === lower) || (r.title && r.title.toLowerCase().includes(lower)) || String(r.role_id) === role);
                            if (found) roleId = found.role_id;
                        }
                    } catch (e) {
                        // ignore lookup failures, we'll handle missing roleId below
                        console.warn('Role lookup failed', e);
                    }
                }
            }

            // If not resolved yet, try roleSelect value (populated on load)
            if (!roleId && roleSelect && roleSelect.value) {
                roleId = parseInt(roleSelect.value, 10);
            }

            if (!roleId) {
                showStatus('Role not found or unspecified; please pick a role before saving feedback', false);
                return;
            }
            // Create interview first (backend will validate recruiter via RECRUITER_ID global)
            const createUrl = `${API_BASE}/recruiters/${RECRUITER_ID}/interviews`;
            let createRes;
            try {
                createRes = await fetch(createUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ candidate_id: parseInt(candidateId, 10), role_id: roleId })
            });
            } catch (networkErr) {
                // network-level error (DNS, CORS blocked, offline)
                throw new Error(`Network error contacting API (${createUrl}): ${networkErr.message}`);
            }
            if (!createRes.ok) {
                const err = await createRes.json().catch(() => ({}));
                // Normalize detail which can be a string, an object or an array (pydantic validation errors)
                let detailMsg = err.detail || `Status ${createRes.status}`;
                if (Array.isArray(detailMsg) || typeof detailMsg === 'object') {
                    try { detailMsg = JSON.stringify(detailMsg); } catch (e) { detailMsg = String(detailMsg); }
                }
                throw new Error(detailMsg);
            }
            const createData = await createRes.json();
            const interviewId = createData.interview_id;

            const noteUrl = `${API_BASE}/recruiters/${RECRUITER_ID}/interviews/${interviewId}/notes`;
            let noteRes;
            try {
                noteRes = await fetch(noteUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ notes, fit_score: rating, role_id: roleId })
                });
            } catch (networkErr) {
                throw new Error(`Network error contacting API (${noteUrl}): ${networkErr.message}`);
            }
            if (!noteRes.ok) {
                const err = await noteRes.json().catch(() => ({}));
                let detailMsg = err.detail || `Status ${noteRes.status}`;
                if (Array.isArray(detailMsg) || typeof detailMsg === 'object') {
                    try { detailMsg = JSON.stringify(detailMsg); } catch (e) { detailMsg = String(detailMsg); }
                }
                throw new Error(detailMsg);
            }

            // Show a persistent saved message and keep the form inputs intact.
            showStatus('Feedback saved — your inputs are preserved');

            // add persistent action buttons: Back to interviews and Continue editing
            let actionsWrap = document.getElementById('saveActions');
            if (!actionsWrap) {
                actionsWrap = document.createElement('div');
                actionsWrap.id = 'saveActions';
                actionsWrap.style.marginTop = '8px';
                status.insertAdjacentElement('afterend', actionsWrap);
            } else {
                actionsWrap.innerHTML = '';
            }

            const backBtn = document.createElement('button');
            backBtn.type = 'button';
            backBtn.className = 'secondary';
            backBtn.textContent = 'Back to interviews';
            backBtn.onclick = () => { window.location.href = '../../pages/recruiter/interviews.html'; };

            const continueBtn = document.createElement('button');
            continueBtn.type = 'button';
            continueBtn.className = 'primary';
            continueBtn.style.marginLeft = '8px';
            continueBtn.textContent = 'Continue editing';
            continueBtn.onclick = () => {
                // simply remove the action buttons and keep the inputs as-is
                actionsWrap.remove();
                showStatus('Feedback saved — you can continue editing');
            };

            actionsWrap.appendChild(backBtn);
            actionsWrap.appendChild(continueBtn);

            // determine role title if available
            let role_title = null;
            try {
                if (roleSelect && roleSelect.value) role_title = roleSelect.selectedOptions[0].textContent;
                else if (role && typeof role === 'string') role_title = role;
            } catch (e) { role_title = null; }

            // record saved note so it can survive reloads and be previewed (include role info)
            try { saveSavedRecord(notes, rating, interviewId, roleId, role_title); } catch (e) { console.warn('Failed to persist saved record', e); }

        } catch (err) {
            console.error('Save feedback failed', err);
            // Friendly message for common network error
            if (err.message && err.message.toLowerCase().includes('network error')) {
                showStatus('Failed to save feedback: network error — check backend is running and accessible', false);
            } else {
                showStatus('Failed to save feedback: ' + err.message, false);
            }
        } finally {
            // re-enable the button so user can retry; do not clear inputs
            saveBtn.disabled = false;
        }
    });
});
