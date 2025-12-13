document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".lesson").forEach(lesson => {
        lesson.addEventListener("click", () => {
            lesson.classList.toggle("completed");

            const path = lesson.closest(".path");
            const lessons = path.querySelectorAll(".lesson");
            const tests = path.querySelectorAll(".test");

            const allCompleted = [...lessons].every(l =>
                l.classList.contains("completed")
            );

            tests.forEach(test => {
                test.classList.toggle("locked", !allCompleted);
                test.classList.toggle("unlocked", allCompleted);
            });
        });
    });

});
