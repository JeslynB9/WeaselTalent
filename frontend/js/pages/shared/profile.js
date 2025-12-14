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

    // technical domains logic
    const selectedDomains = new Set();

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
