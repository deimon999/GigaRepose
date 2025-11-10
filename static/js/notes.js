// Notes Management
let currentNotes = [];
let currentEditingNoteId = null;

// Initialize notes when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadNotes();
    setupNotesEventListeners();
});

function setupNotesEventListeners() {
    // Toggle notes panel
    const notesToggle = document.getElementById('notesToggle');
    if (notesToggle) {
        notesToggle.addEventListener('click', toggleNotesPanel);
    }
    
    // New note button
    const newNoteBtn = document.getElementById('newNoteBtn');
    if (newNoteBtn) {
        newNoteBtn.addEventListener('click', showNewNoteForm);
    }
    
    // Save note button
    const saveNoteBtn = document.getElementById('saveNoteBtn');
    if (saveNoteBtn) {
        saveNoteBtn.addEventListener('click', saveNote);
    }
    
    // Cancel note button
    const cancelNoteBtn = document.getElementById('cancelNoteBtn');
    if (cancelNoteBtn) {
        cancelNoteBtn.addEventListener('click', cancelNoteEdit);
    }
    
    // Search notes
    const searchNotesInput = document.getElementById('searchNotes');
    if (searchNotesInput) {
        searchNotesInput.addEventListener('input', (e) => {
            filterNotes(e.target.value);
        });
    }
}

function toggleNotesPanel() {
    const notesPanel = document.getElementById('notesPanel');
    if (notesPanel) {
        notesPanel.classList.toggle('hidden');
        if (!notesPanel.classList.contains('hidden')) {
            loadNotes();
        }
    }
}

async function loadNotes() {
    try {
        const response = await fetch('/notes');
        const data = await response.json();
        
        if (data.status === 'success') {
            currentNotes = data.notes;
            renderNotesList();
        } else {
            console.error('Error loading notes:', data.error);
        }
    } catch (error) {
        console.error('Error loading notes:', error);
    }
}

function renderNotesList() {
    const notesListContainer = document.getElementById('notesList');
    if (!notesListContainer) return;
    
    if (currentNotes.length === 0) {
        notesListContainer.innerHTML = `
            <div class="empty-notes">
                <p>📝 No notes yet</p>
                <p>Click "New Note" to get started!</p>
            </div>
        `;
        return;
    }
    
    notesListContainer.innerHTML = currentNotes.map(note => `
        <div class="note-item" data-note-id="${note.id}">
            <div class="note-header">
                <h4 class="note-title">${escapeHtml(note.title)}</h4>
                <span class="note-category">${escapeHtml(note.category)}</span>
            </div>
            <p class="note-content-preview">${escapeHtml(truncateText(note.content, 100))}</p>
            <div class="note-footer">
                <span class="note-date">${formatDate(note.updated_at)}</span>
                <div class="note-actions">
                    <button class="note-action-btn" onclick="editNote(${note.id})" title="Edit">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                    </button>
                    <button class="note-action-btn delete" onclick="deleteNote(${note.id})" title="Delete">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function showNewNoteForm() {
    currentEditingNoteId = null;
    document.getElementById('noteTitle').value = '';
    document.getElementById('noteContent').value = '';
    document.getElementById('noteCategory').value = 'General';
    document.getElementById('noteFormContainer').classList.remove('hidden');
    document.getElementById('notesList').classList.add('hidden');
    document.getElementById('noteFormTitle').textContent = 'New Note';
}

async function editNote(noteId) {
    try {
        const response = await fetch(`/notes/${noteId}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            currentEditingNoteId = noteId;
            document.getElementById('noteTitle').value = data.note.title;
            document.getElementById('noteContent').value = data.note.content;
            document.getElementById('noteCategory').value = data.note.category;
            document.getElementById('noteFormContainer').classList.remove('hidden');
            document.getElementById('notesList').classList.add('hidden');
            document.getElementById('noteFormTitle').textContent = 'Edit Note';
        }
    } catch (error) {
        console.error('Error loading note:', error);
        alert('Failed to load note');
    }
}

async function saveNote() {
    const title = document.getElementById('noteTitle').value.trim() || 'Untitled Note';
    const content = document.getElementById('noteContent').value.trim();
    const category = document.getElementById('noteCategory').value;
    
    if (!content) {
        alert('Note content cannot be empty');
        return;
    }
    
    try {
        let response;
        
        if (currentEditingNoteId) {
            // Update existing note
            response = await fetch(`/notes/${currentEditingNoteId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ title, content, category })
            });
        } else {
            // Create new note
            response = await fetch('/notes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ title, content, category })
            });
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            cancelNoteEdit();
            loadNotes();
            showNotification(data.message, 'success');
        } else {
            alert('Error saving note: ' + data.error);
        }
    } catch (error) {
        console.error('Error saving note:', error);
        alert('Failed to save note');
    }
}

async function deleteNote(noteId) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }
    
    try {
        const response = await fetch(`/notes/${noteId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            loadNotes();
            showNotification(data.message, 'success');
        } else {
            alert('Error deleting note: ' + data.error);
        }
    } catch (error) {
        console.error('Error deleting note:', error);
        alert('Failed to delete note');
    }
}

function cancelNoteEdit() {
    currentEditingNoteId = null;
    document.getElementById('noteFormContainer').classList.add('hidden');
    document.getElementById('notesList').classList.remove('hidden');
}

function filterNotes(query) {
    if (!query.trim()) {
        renderNotesList();
        return;
    }
    
    const filtered = currentNotes.filter(note => 
        note.title.toLowerCase().includes(query.toLowerCase()) ||
        note.content.toLowerCase().includes(query.toLowerCase()) ||
        note.category.toLowerCase().includes(query.toLowerCase())
    );
    
    const notesListContainer = document.getElementById('notesList');
    if (!notesListContainer) return;
    
    if (filtered.length === 0) {
        notesListContainer.innerHTML = `
            <div class="empty-notes">
                <p>🔍 No notes found</p>
                <p>Try a different search term</p>
            </div>
        `;
        return;
    }
    
    // Render filtered notes (reuse renderNotesList logic)
    const temp = currentNotes;
    currentNotes = filtered;
    renderNotesList();
    currentNotes = temp;
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}

function showNotification(message, type = 'info') {
    // Reuse existing notification system if available
    if (typeof addMessage === 'function') {
        const icon = type === 'success' ? '✓' : 'ℹ';
        console.log(`${icon} ${message}`);
    }
}
