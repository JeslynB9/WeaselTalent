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

});

/* Visual state */
function toggleVisualState(card, isVisible) {
    card.classList.toggle("hidden", !isVisible);
}

/* Placeholder for backend integration */
function persistSkill(skillName, isVisible) {
    console.log(`Skill: ${skillName}, Visible: ${isVisible}`);

    // Later:
    // fetch("/api/profile/skills", {
    //     method: "POST",
    //     body: JSON.stringify({ skillName, isVisible })
    // });
}


const anonToggle = document.getElementById("anon-toggle");

anonToggle.addEventListener("change", () => {
    console.log("Anonymous profile:", anonToggle.checked);
});