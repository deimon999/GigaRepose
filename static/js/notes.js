// Simple Notes Management
let currentNotes = [];
let currentEditingNoteId = null;
let notesListenersSetup = false;

console.log('Notes.js loaded');

// This function will be called by app.js when Notes panel opens
function setupNotesEventListeners() {
    console.log('Setting up notes listeners...');
    
    // Always reload notes when panel opens
    loadNotes();
    
    // Only set up event listeners once
    if (notesListenersSetup) {
        console.log('Notes listeners already set up, just reloaded data');
        return;
    }
    notesListenersSetup = true;
}

async function loadNotes() {
    console.log('Loading notes...');
    try {
        const response = await fetch('/notes');
        const data = await response.json();
        if (data.status === 'success') {
            currentNotes = data.notes;
            console.log('Loaded notes:', currentNotes.length);
            renderNotesList();
        }
    } catch (error) {
        console.error('Error loading notes:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to load notes', 'error');
        }
    }
}

function renderNotesList() {
    const container = document.getElementById('notesList');
    if (!container) {
        console.error('notesList container not found');
        return;
    }
    
    if (currentNotes.length === 0) {
        container.innerHTML = `
            <div style="text-align:center;padding:40px;color:#888;">
                <p style="font-size:3rem;"></p>
                <p>No notes yet</p>
                <p style="font-size:0.9rem;margin-top:10px;">Click "+ New Note" to create one</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = currentNotes.map(note => `
        <div class="note-item" onclick="viewNote(${note.id})">
            <div class="note-title">${escapeHtml(note.title)}</div>
            <div class="note-preview">${escapeHtml(truncate(note.content, 100))}</div>
            <div class="note-meta">
                <span>${note.category || 'General'}</span>
                <span>${new Date(note.created_at).toLocaleDateString()}</span>
            </div>
            <div style="margin-top:8px;">
                <button onclick="event.stopPropagation();editNoteForm(${note.id})" style="background:#4ecca3;color:white;border:none;padding:4px 12px;border-radius:5px;cursor:pointer;margin-right:5px;">Edit</button>
                <button onclick="event.stopPropagation();confirmDeleteNote(${note.id})" style="background:#ff6b6b;color:white;border:none;padding:4px 12px;border-radius:5px;cursor:pointer;">Delete</button>
            </div>
        </div>
    `).join('');
}

function showNewNoteForm() {
    console.log('Show new note form');
    currentEditingNoteId = null;
    document.getElementById('noteTitle').value = '';
    document.getElementById('noteContent').value = '';
    document.getElementById('noteCategory').value = 'General';
    document.getElementById('noteFormTitle').textContent = 'New Note';
    document.getElementById('noteFormContainer').classList.remove('hidden');
    document.getElementById('notesList').classList.add('hidden');
}

function viewNote(noteId) {
    console.log('View note:', noteId);
    const note = currentNotes.find(n => n.id === noteId);
    if (note) {
        if (typeof showModal === 'function') {
            showModal(note.title, note.content);
        } else {
            alert(`${note.title}\n\n${note.content}`);
        }
    }
}

function editNoteForm(noteId) {
    console.log('Edit note:', noteId);
    const note = currentNotes.find(n => n.id === noteId);
    if (!note) return;
    
    currentEditingNoteId = noteId;
    document.getElementById('noteTitle').value = note.title;
    document.getElementById('noteContent').value = note.content;
    document.getElementById('noteCategory').value = note.category || 'General';
    document.getElementById('noteFormTitle').textContent = 'Edit Note';
    document.getElementById('noteFormContainer').classList.remove('hidden');
    document.getElementById('notesList').classList.add('hidden');
}

async function saveNote() {
    console.log('Save note');
    const title = document.getElementById('noteTitle').value.trim() || 'Untitled';
    const content = document.getElementById('noteContent').value.trim();
    const category = document.getElementById('noteCategory').value;
    
    if (!content) {
        if (typeof showToast === 'function') {
            showToast('Content cannot be empty', 'error');
        } else {
            alert('Content cannot be empty');
        }
        return;
    }
    
    try {
        const url = currentEditingNoteId ? `/notes/${currentEditingNoteId}` : '/notes';
        const method = currentEditingNoteId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, category })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            if (typeof showToast === 'function') {
                showToast(currentEditingNoteId ? 'Note updated!' : 'Note created!', 'success');
            }
            cancelNoteEdit();
            await loadNotes();
        } else {
            throw new Error(data.error || 'Failed to save note');
        }
    } catch (error) {
        console.error('Save error:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to save note: ' + error.message, 'error');
        } else {
            alert('Failed to save note: ' + error.message);
        }
    }
}

function cancelNoteEdit() {
    console.log('Cancel note edit');
    currentEditingNoteId = null;
    document.getElementById('noteFormContainer').classList.add('hidden');
    document.getElementById('notesList').classList.remove('hidden');
}

function confirmDeleteNote(noteId) {
    console.log('Confirm delete note:', noteId);
    const note = currentNotes.find(n => n.id === noteId);
    if (note && confirm(`Delete "${note.title}"?`)) {
        deleteNoteById(noteId);
    }
}

async function deleteNoteById(noteId) {
    console.log('Delete note:', noteId);
    try {
        const response = await fetch(`/notes/${noteId}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.status === 'success') {
            if (typeof showToast === 'function') {
                showToast('Note deleted!', 'success');
            }
            await loadNotes();
        } else {
            throw new Error(data.error || 'Failed to delete note');
        }
    } catch (error) {
        console.error('Delete error:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to delete note: ' + error.message, 'error');
        } else {
            alert('Failed to delete note: ' + error.message);
        }
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncate(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Expose functions globally for onclick handlers and app.js
window.setupNotesEventListeners = setupNotesEventListeners;
window.showNewNoteForm = showNewNoteForm;
window.saveNote = saveNote;
window.cancelNoteEdit = cancelNoteEdit;
window.viewNote = viewNote;
window.editNoteForm = editNoteForm;
window.confirmDeleteNote = confirmDeleteNote;
