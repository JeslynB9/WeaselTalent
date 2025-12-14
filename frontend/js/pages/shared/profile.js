// technical domains logic
const selectedDomains = new Set();

const candidateId = params.get('candidate_id') || localStorage.getItem('user_id');

document.addEventListener("DOMContentLoaded", () => {

    const skillCards = document.querySelectorAll(".skill-card");

    skillCards.forEach(card => {
        const checkbox = card.querySelector("input[type='checkbox']");

        // Initial state
        toggleVisualState(card, checkbox.checked);

        // Clicking the toggle
        checkbox.addEventListener("change", (e) => {
            e.stopPropagation(); // prevent double toggle
            toggleVisualState(card, checkbox.checked);
            persistSkill(card.dataset.skill, checkbox.checked);
        });

        // Clicking anywhere on the card
        card.addEventListener("click", () => {
            checkbox.checked = !checkbox.checked;
            toggleVisualState(card, checkbox.checked);
            persistSkill(card.dataset.skill, checkbox.checked);
        });
    });

    document.querySelectorAll(".domain.selected").forEach(el => {
        selectedDomains.add(el.dataset.domain);
    });

    document.querySelectorAll(".domain").forEach(domainEl => {
        domainEl.addEventListener("click", () => {
            const domain = domainEl.dataset.domain;

            if (selectedDomains.has(domain)) {
                selectedDomains.delete(domain);
                domainEl.classList.remove("selected");
            } else {
                selectedDomains.add(domain);
                domainEl.classList.add("selected");
            }

            console.log("Selected domains:", [...selectedDomains]);
        })
    })

    // save button
    const saveSkillsBtn = document.getElementById("save-skills");
    if (saveSkillsBtn) {
        saveSkillsBtn.addEventListener("click", () => {
            console.log("Saving domains:", [...selectedDomains]);
        });
    }

    async function loadSavedDomains() {
        try {
            const res = await fetch(
            `http://127.0.0.1:8000/candidate/domains/${userId}`
            );

            const domains = await res.json();

            selectedDomains.clear();
            domains.forEach(d => selectedDomains.add(d));

            document.querySelectorAll(".domain").forEach(el => {
            el.classList.toggle(
                "selected",
                selectedDomains.has(el.dataset.domain)
            );
            });

            console.log("Loaded domains from backend:", domains);
        } catch (err) {
            console.error("Failed to load domains", err);
        }
    }

    loadSavedDomains();

    const user = JSON.parse(localStorage.getItem("user"));
    const userId = user.user_id;

    const saveBtn = document.getElementById("save-skills");

    saveBtn.addEventListener("click", async () => {
    try {
        await fetch("http://127.0.0.1:8000/candidate/domains", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            user_id: userId,
            domains: [...selectedDomains],
        }),
        });

        alert("Skills saved!");
        } catch (err) {
            console.error(err);
            alert("Failed to save skills");
        }
    });
});

function toggleVisualState(card, isVisible) {
    card.classList.toggle("hidden", !isVisible);
}

function persistSkill(skillName, isVisible) {
    console.log(`Skill: ${skillName}, Visible: ${isVisible}`);
}

const anonToggle = document.getElementById("anon-toggle");
if (anonToggle) {
    anonToggle.addEventListener("change", () => {
        console.log("Anonymous profile:", anonToggle.checked);
    });
}

