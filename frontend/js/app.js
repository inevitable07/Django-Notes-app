/**
 * Notes App — Frontend Logic
 *
 * Handles CRUD operations against the Django REST API,
 * modal management, and DOM updates.
 */

// ════════════════════════════════════════════════════
// Configuration
// ════════════════════════════════════════════════════
const API_BASE = "http://127.0.0.1:8000/api";
const ENDPOINTS = {
  notes: `${API_BASE}/notes/`,
  deleteNote: (id) => `${API_BASE}/notes/${id}/`,
};


// ════════════════════════════════════════════════════
// DOM References
// ════════════════════════════════════════════════════
const notesList     = document.getElementById("notes-list");
const emptyState    = document.getElementById("empty-state");
const loader        = document.getElementById("loader");
const fab           = document.getElementById("fab-add");
const modalOverlay  = document.getElementById("modal-overlay");
const modal         = document.getElementById("modal");
const modalClose    = document.getElementById("modal-close");
const noteForm      = document.getElementById("note-form");
const titleInput    = document.getElementById("note-title");
const contentInput  = document.getElementById("note-content");
const titleCount    = document.getElementById("title-count");
const formError     = document.getElementById("form-error");
const btnSave       = document.getElementById("btn-save");
const toast         = document.getElementById("toast");


// ════════════════════════════════════════════════════
// State
// ════════════════════════════════════════════════════
let toastTimer = null;


// ════════════════════════════════════════════════════
// API Helpers
// ════════════════════════════════════════════════════

/**
 * Fetch all notes from the API.
 * @returns {Promise<Array>} Array of note objects.
 */
async function fetchNotes() {
  const res = await fetch(ENDPOINTS.notes);
  if (!res.ok) throw new Error(`Failed to fetch notes (${res.status})`);
  return res.json();
}

/**
 * Create a new note via the API.
 * @param {string} title
 * @param {string} content
 * @returns {Promise<Object>} Created note object.
 */
async function createNote(title, content) {
  const res = await fetch(ENDPOINTS.notes, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content }),
  });

  const data = await res.json();

  if (!res.ok) {
    // Build a readable error from DRF validation errors
    const messages = Object.values(data).flat().join(", ");
    throw new Error(messages || "Failed to create note");
  }

  return data;
}

/**
 * Delete a note by ID.
 * @param {number} id
 */
async function removeNote(id) {
  const res = await fetch(ENDPOINTS.deleteNote(id), { method: "DELETE" });
  if (!res.ok && res.status !== 204) {
    throw new Error(`Failed to delete note (${res.status})`);
  }
}


// ════════════════════════════════════════════════════
// UI Rendering
// ════════════════════════════════════════════════════

/**
 * Format an ISO date string into a human-friendly format.
 * @param {string} isoString
 * @returns {string}
 */
function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Create a note card DOM element.
 * @param {Object} note
 * @returns {HTMLElement}
 */
function createNoteCard(note) {
  const card = document.createElement("article");
  card.className = "note-card";
  card.dataset.id = note.id;

  card.innerHTML = `
    <h3 class="note-title">${escapeHtml(note.title)}</h3>
    <p class="note-content">${escapeHtml(note.content)}</p>
    <div class="note-footer">
      <time class="note-date" datetime="${note.created_at}">
        ${formatDate(note.created_at)}
      </time>
    </div>
    <button class="btn-delete" aria-label="Delete note: ${escapeHtml(note.title)}" title="Delete">
      🗑️
    </button>
  `;

  // Attach delete handler
  const deleteBtn = card.querySelector(".btn-delete");
  deleteBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    deleteNote(note.id, card);
  });

  return card;
}

/**
 * Escape HTML to prevent XSS.
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Toggle visibility between the notes list and empty state.
 * @param {number} count
 */
function toggleEmptyState(count) {
  if (count === 0) {
    emptyState.classList.add("visible");
    notesList.style.display = "none";
  } else {
    emptyState.classList.remove("visible");
    notesList.style.display = "flex";
  }
}


// ════════════════════════════════════════════════════
// Core Actions
// ════════════════════════════════════════════════════

/**
 * Load all notes and render them.
 */
async function loadNotes() {
  loader.classList.add("visible");
  notesList.innerHTML = "";
  emptyState.classList.remove("visible");

  try {
    const notes = await fetchNotes();

    loader.classList.remove("visible");
    toggleEmptyState(notes.length);

    notes.forEach((note) => {
      notesList.appendChild(createNoteCard(note));
    });
  } catch (err) {
    loader.classList.remove("visible");
    showToast("Could not load notes. Is the server running?", "error");
    console.error("loadNotes error:", err);
  }
}

/**
 * Validate inputs, create a note, then refresh the list.
 */
async function addNote() {
  const title = titleInput.value.trim();
  const content = contentInput.value.trim();

  // Client-side validation
  if (!title) {
    showFormError("Please enter a title.");
    titleInput.focus();
    return;
  }
  if (!content) {
    showFormError("Please enter some content.");
    contentInput.focus();
    return;
  }

  clearFormError();
  setButtonLoading(true);

  try {
    await createNote(title, content);
    closeModal();
    showToast("Note created! ✨", "success");
    await loadNotes();
  } catch (err) {
    showFormError(err.message);
    console.error("addNote error:", err);
  } finally {
    setButtonLoading(false);
  }
}

/**
 * Delete a note with a smooth exit animation.
 * @param {number} id
 * @param {HTMLElement} cardEl
 */
async function deleteNote(id, cardEl) {
  // Animate out
  cardEl.classList.add("deleting");

  try {
    await removeNote(id);

    // Wait for animation to finish, then remove from DOM
    cardEl.addEventListener("animationend", () => {
      cardEl.remove();
      toggleEmptyState(notesList.children.length);
    });

    showToast("Note deleted", "success");
  } catch (err) {
    // Undo the animation on failure
    cardEl.classList.remove("deleting");
    showToast("Failed to delete note", "error");
    console.error("deleteNote error:", err);
  }
}


// ════════════════════════════════════════════════════
// Modal Controls
// ════════════════════════════════════════════════════

/** Open the "New Note" modal. */
function openModal() {
  noteForm.reset();
  clearFormError();
  updateTitleCount();
  modalOverlay.classList.add("active");
  // Focus the title input after the transition
  setTimeout(() => titleInput.focus(), 300);
  // Prevent body scroll
  document.body.style.overflow = "hidden";
}

/** Close the modal. */
function closeModal() {
  modalOverlay.classList.remove("active");
  document.body.style.overflow = "";
}


// ════════════════════════════════════════════════════
// Form Helpers
// ════════════════════════════════════════════════════

/** Show a validation error below the form. */
function showFormError(message) {
  formError.textContent = message;
}

/** Clear the form error. */
function clearFormError() {
  formError.textContent = "";
}

/** Toggle save button loading state. */
function setButtonLoading(isLoading) {
  btnSave.disabled = isLoading;
  btnSave.classList.toggle("loading", isLoading);
}

/** Update the character counter for the title. */
function updateTitleCount() {
  const len = titleInput.value.length;
  titleCount.textContent = `${len} / 100`;
}


// ════════════════════════════════════════════════════
// Toast Notification
// ════════════════════════════════════════════════════

/**
 * Show a toast notification.
 * @param {string} message
 * @param {"success"|"error"} type
 */
function showToast(message, type = "success") {
  // Clear any pending toast
  if (toastTimer) clearTimeout(toastTimer);

  toast.textContent = message;
  toast.className = "toast visible " + type;

  toastTimer = setTimeout(() => {
    toast.classList.remove("visible");
  }, 2800);
}


// ════════════════════════════════════════════════════
// Event Listeners
// ════════════════════════════════════════════════════

// FAB → open modal
fab.addEventListener("click", openModal);

// Close modal via ✕ button
modalClose.addEventListener("click", closeModal);

// Close modal when clicking the overlay (outside the modal card)
modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) closeModal();
});

// Close modal on Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modalOverlay.classList.contains("active")) {
    closeModal();
  }
});

// Form submission
noteForm.addEventListener("submit", (e) => {
  e.preventDefault();
  addNote();
});

// Title character counter
titleInput.addEventListener("input", updateTitleCount);


// ════════════════════════════════════════════════════
// Initialization
// ════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", loadNotes);
