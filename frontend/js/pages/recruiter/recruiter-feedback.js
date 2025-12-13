document.addEventListener("DOMContentLoaded", () => {
    const saveNoteBtn = document.getElementById("saveNoteBtn");
    const notes = document.getElementById("notes");

    if (!saveNoteBtn || !notes) return;

    saveNoteBtn.addEventListener("click", () => {
        // placeholder: save note locally
        const text = notes.value.trim();
        if (!text) return alert('Please enter a note');
        alert('Note saved (demo)');
    });
});
