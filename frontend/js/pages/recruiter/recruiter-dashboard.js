async function fetchPipeline(roleId = null) {
  let url = `${API_BASE}/recruiters/${RECRUITER_ID}/pipeline`;
  if (roleId) url += `?role_id=${roleId}`;

  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to load pipeline");

  return await res.json();
}

async function renderList() {
  const items = await fetchPipeline();

  const list = document.getElementById("list");
  list.innerHTML = "";

  items.forEach(c => {
    list.innerHTML += `
      <div class="cand">
        <div>${c.display_name}</div>
        <div>${c.role_title}</div>
        <div>${Math.round(c.match_score)}%</div>
        <div>
          <button onclick="openCandidate(${c.candidate_id})">Review</button>
        </div>
      </div>
    `;
  });
}

async function openCandidate(candidateId) {
  const res = await fetch(
    `${API_BASE}/recruiters/${RECRUITER_ID}/candidates/${candidateId}`
  );
  const data = await res.json();

  document.getElementById("drawer").classList.remove("hidden");

  document.getElementById("drawer").innerHTML = `
    <h3>${data.isAnonymous ? "Anonymous Candidate" : data.name}</h3>
  `;
}

async function addAvailability(start, end) {
  await fetch(`${API_BASE}/recruiters/${RECRUITER_ID}/availability`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      start_time: start,
      end_time: end
    })
  });
}


// ---------------------------
// API Integration
// ---------------------------

async function fetchCandidates() {
    try {
        const response = await fetch(`${API_BASE}/recruiters/1/pipeline`);
        if (!response.ok) throw new Error('Failed to fetch candidates');
        const data = await response.json();
        // Map to expected format (adjust based on backend response)
        return data.map(item => ({
            id: item.candidate_id.toString(),
            lastActive: item.last_updated,
            skills: [], // Add if available
            domains: [], // Add if available
            assessments: [] // Add if available
        }));
    } catch (error) {
        console.error('Error fetching candidates:', error);
        return CANDIDATES; // Fallback to mock
    }
}

async function fetchJobs() {
    // For now, return mock; add endpoint if needed
    return JOBS;
}

const $ = (id) => document.getElementById(id);

function scoreColor(score) {
    if (score >= 80) return "ok";
    if (score >= 60) return "mid";
    return "bad";
}

function toHumanDate(iso) {
    const d = new Date(iso);
    return d.toLocaleString(undefined, { weekday: "short", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function computeMatchScore(candidate, job) {
    const req = job.requirements.map(r => r.toLowerCase());
    const skills = candidate.skills.map(s => s.toLowerCase());

    let matches = 0;
    req.forEach(r => {
    if (skills.some(s => s.includes(r) || r.includes(s))) matches++;
    });

    const total = req.length || 1;
    let score = Math.round((matches / total) * 100);
    if (score > 95) score = 95;
    return { score, matches, total };
}

function overallAssessmentPercent(candidate) {
    const totals = candidate.assessments.reduce((acc, a) => {
    acc.score += a.score; acc.total += a.total;
    return acc;
    }, { score: 0, total: 0 });

    if (!totals.total) return 0;
    return Math.round((totals.score / totals.total) * 100);
}

function uniqDomains() {
    const s = new Set();
    CANDIDATES.forEach(c => c.domains.forEach(d => s.add(d)));
    return Array.from(s).sort();
}

function showStatus(text) {
    const el = $("status");
    el.textContent = text;
    el.classList.remove("hidden");
    setTimeout(() => el.classList.add("hidden"), 2200);
}

// ---------------------------
// Render controls
// ---------------------------

function initJobs() {
    $("jobSelect").innerHTML = JOBS.map(j => `<option value="${j.id}">${j.title}</option>`).join("");
    if (JOBS.length > 0) {
        $("jobSelect").value = JOBS[0].id; // Set default to first job
    }
}

function initDomainFilter() {
    const doms = uniqDomains();
    $("domainFilter").innerHTML = `<option value="ALL">Domain: All</option>` + doms.map(d => `<option value="${d}">${d}</option>`).join("");
}

function renderSlots() {
    const container = $("slots");
    if (!availability.length) {
    container.innerHTML = `<div class="muted">No availability yet.</div>`;
    return;
    }
    container.innerHTML = availability.map(s => `
        <div class="slot">
            <span>${s.day} ${s.start}–${s.end}</span>
            <button class="btn-remove" data-del="${s.id}">Remove</button>
        </div>
    `).join("");

    container.querySelectorAll("[data-del]").forEach(el => {
    el.addEventListener("click", () => {
        const id = el.getAttribute("data-del");
        availability = availability.filter(x => x.id !== id);
        renderSlots();
        showStatus("Availability removed.");
    });
    });
}

// ---------------------------
// Render candidate list
// ---------------------------

function getFilteredCandidates() {
    const job = JOBS.find(j => j.id === $("jobSelect").value);
    const minScore = Number($("minScore").value);
    const domain = $("domainFilter").value;
    const sortBy = $("sortBy").value;
    const q = $("search").value.trim().toLowerCase();

    let items = CANDIDATES.map(c => {
    const ms = computeMatchScore(c, job);
    return { ...c, matchScore: ms.score, matchMeta: ms };
    });

    items = items.filter(c => c.matchScore >= minScore);

    if (domain !== "ALL") {
    items = items.filter(c => c.domains.includes(domain));
    }

    if (q) {
    items = items.filter(c =>
        c.id.toLowerCase().includes(q) ||
        c.skills.some(s => s.toLowerCase().includes(q)) ||
        c.domains.some(d => d.toLowerCase().includes(q))
    );
    }

    if (sortBy === "scoreDesc") items.sort((a,b) => b.matchScore - a.matchScore);
    if (sortBy === "scoreAsc") items.sort((a,b) => a.matchScore - b.matchScore);
    if (sortBy === "recentDesc") items.sort((a,b) => new Date(b.lastActive) - new Date(a.lastActive));

    return items;
}

function renderList() {
    const job = JOBS.find(j => j.id === $("jobSelect").value);
    const items = getFilteredCandidates();

    $("meta").textContent = `${items.length} candidates shown • Job requirements: ${job.requirements.join(", ")}`;

    const list = $("list");
    if (!items.length) {
    list.innerHTML = `<div class="muted">No candidates match your filters.</div>`;
    return;
    }

    list.innerHTML = items.map(c => {
    const assessPct = overallAssessmentPercent(c);
    const scoreClass = scoreColor(c.matchScore);

    return `
        <div class="cand">
        <div>
            <strong>${c.id}</strong>
            <div class="muted">Last active: ${toHumanDate(c.lastActive)}</div>
        </div>

        <div>
            <div>${c.domains.join(", ")}</div>
            <div class="small">Skills: ${c.skills.join(", ")}</div>
        </div>

        <div>
            <strong>${assessPct}%</strong>
            <div class="small">${c.assessments.length} assessments</div>
        </div>

        <div class="score ${scoreClass}">
            ${c.matchScore}%
            <div class="small">${c.matchMeta.matches}/${c.matchMeta.total} overlap</div>
        </div>

        <button class="primary">Review</button>
        </div>
    `;
    }).join("");

    list.querySelectorAll("[data-open]").forEach(btn => {
    btn.addEventListener("click", () => openDrawer(btn.getAttribute("data-open")));
    });
}

// ---------------------------
// Drawer (candidate review)
// ---------------------------

let activeCandidateId = null;

function renderSlotPicker() {
    const pick = $("slotPick");
    if (!availability.length) {
    pick.innerHTML = `<option value="">No availability slots</option>`;
    return;
    }
    pick.innerHTML = availability.map(s => `<option value="${s.id}">${s.day} ${s.start}–${s.end}</option>`).join("");
}

function openDrawer(candidateId) {
    activeCandidateId = candidateId;
    const c = CANDIDATES.find(x => x.id === candidateId);
    const job = JOBS.find(j => j.id === $("jobSelect").value);

    const ms = computeMatchScore(c, job);
    const drawerContent = `
        <button id="closeDrawerBtn" style="float:right;">Close</button>
        <h3>Candidate Review</h3>
        <div id="drawerMeta"></div>
        <div class="divider"></div>
        <h4>Assessments</h4>
        <div id="assessmentsBox"></div>
        <div id="assessmentsDetail"></div>
        <div class="divider"></div>
        <h4>Notes</h4>
        <div class="row">
            <input id="rating" type="number" min="1" max="10" placeholder="Rating (1-10)" />
            <textarea id="notes" placeholder="Notes..."></textarea>
        </div>
        <button id="saveNoteBtn">Save Notes</button>
        <div class="divider"></div>
        <div id="savedNotes" class="muted"></div>
        <div class="divider"></div>
        <h4>Schedule Interview</h4>
        <select id="slotPick"></select>
        <button id="bookBtn">Book Interview</button>
        <div id="bookingStatus"></div>
    `;
    $("drawer").innerHTML = drawerContent;

    // Now set the content
    $("drawerMeta").innerHTML = `
    <div class="pill">Candidate: <strong>${c.id}</strong></div>
    <div class="pill">Job: <strong>${job.title}</strong></div>
    <div class="pill">Match: <strong class="${scoreColor(ms.score)}">${ms.score}%</strong></div>
    <div class="pill">Last active: <strong>${toHumanDate(c.lastActive)}</strong></div>
    `;

    $("assessmentsDetail").innerHTML = c.assessments.map(a => {
    const pct = Math.round((a.score / a.total) * 100);
    return `
        <div class="q">
        <div><strong>${a.domain}</strong> <span class="badge">Level ${a.level}</span></div>
        <div class="muted">Score: ${a.score}/${a.total} (${pct}%)</div>
        </div>
    `;
    }).join("");

    $("assessmentsBox").innerHTML = `<div class="muted">${c.assessments.length} completed • Overall: ${overallAssessmentPercent(c)}%</div>`;

    // Notes
    const saved = NOTES[candidateId];
    $("rating").value = saved?.rating ?? "";
    $("notes").value = saved?.notes ?? "";
    $("savedNotes").textContent = saved
    ? `Rating: ${saved.rating}/10 • Saved: ${toHumanDate(saved.savedAt)}\n\n${saved.notes}`
    : "No notes yet.";

    // Slot picker
    renderSlotPicker();
    $("bookingStatus").textContent = "";

    // Show drawer
    $("drawer").classList.remove("hidden");
    window.scrollTo({ top: $("drawer").offsetTop - 12, behavior: "smooth" });

    // Add event listeners for drawer buttons
    $("closeDrawerBtn").addEventListener("click", closeDrawer);
    $("saveNoteBtn").addEventListener("click", () => {
        if (!activeCandidateId) return;

        const rating = $("rating").value;
        const notes = $("notes").value.trim();

        if (!rating || !notes) {
        return showStatus("Add a rating and notes before saving.");
        }

        NOTES[activeCandidateId] = {
        rating,
        notes,
        savedAt: new Date().toISOString()
        };

        $("savedNotes").textContent = `Rating: ${rating}/10 • Saved: ${toHumanDate(NOTES[activeCandidateId].savedAt)}\n\n${notes}`;
        showStatus("Notes saved.");
    });

    $("bookBtn").addEventListener("click", () => {
        if (!activeCandidateId) return;

        const jobId = $("jobSelect").value;
        const slotId = $("slotPick").value;

        if (!slotId) {
        $("bookingStatus").textContent = "No slot selected.";
        return;
        }

        // Prevent double booking same candidate+job
        const exists = BOOKINGS.some(b => b.candidateId === activeCandidateId && b.jobId === jobId);
        if (exists) {
        $("bookingStatus").textContent = "Already booked for this candidate + job (demo).";
        return;
        }

        const slot = availability.find(s => s.id === slotId);
        BOOKINGS.push({ candidateId: activeCandidateId, jobId, slotId, when: new Date().toISOString() });

        $("bookingStatus").innerHTML = `
        <span class="ok"><strong>Booked!</strong></span>
        Interview scheduled for <strong>${slot.day} ${slot.start}–${slot.end}</strong>.
        `;

        showStatus("Interview booked.");
    });
}

function closeDrawer() {
    activeCandidateId = null;
    $("drawer").classList.add("hidden");
}

// ---------------------------
// Init
// ---------------------------

async function init() {
    // Fetch data from backend
    const jobsData = await fetchJobs();
    window.JOBS = jobsData; // Make global for now
    const candidatesData = await fetchCandidates();
    window.CANDIDATES = candidatesData;

    initJobs();
    initDomainFilter();
    renderSlots();
    renderList();

    // Events
    $("refreshBtn").addEventListener("click", () => {
        showStatus("Refreshed.");
        renderList();
    });

    ["jobSelect","minScore","domainFilter","sortBy"].forEach(id => {
        $(id).addEventListener("change", () => renderList());
    });

    $("search").addEventListener("input", () => renderList());

    $("addSlotBtn").addEventListener("click", () => {
        const day = $("availDay").value;
        const start = $("availStart").value;
        const end = $("availEnd").value;

        if (!start || !end) return showStatus("Please enter start and end time.");
        if (end <= start) return showStatus("End time must be after start time.");

        const id = "slot_" + Math.random().toString(16).slice(2);
        availability.push({ id, day, start, end });
        renderSlots();
        showStatus("Availability added.");
        renderSlotPicker();
    });
}

init();