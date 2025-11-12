// Bookmarks Management
let currentBookmarks = [];
let currentEditingBookmarkId = null;
let bookmarksListenersSetup = false;

console.log('Bookmarks.js loaded');

// This function will be called by app.js when Bookmarks panel opens
function setupBookmarksEventListeners() {
    console.log('Setting up bookmarks listeners...');
    
    // Always reload bookmarks when panel opens
    loadBookmarks();
    
    // Only set up event listeners once
    if (bookmarksListenersSetup) {
        console.log('Bookmarks listeners already set up, just reloaded data');
        return;
    }
    bookmarksListenersSetup = true;
}

async function loadBookmarks() {
    console.log('Loading bookmarks...');
    try {
        const response = await fetch('/bookmarks');
        const data = await response.json();
        if (data.status === 'success') {
            currentBookmarks = data.bookmarks;
            console.log('Loaded bookmarks:', currentBookmarks.length);
            renderBookmarksList();
        }
    } catch (error) {
        console.error('Error loading bookmarks:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to load bookmarks', 'error');
        }
    }
}

function renderBookmarksList() {
    const container = document.getElementById('bookmarksList');
    if (!container) {
        console.error('bookmarksList container not found');
        return;
    }
    
    if (currentBookmarks.length === 0) {
        container.innerHTML = `
            <div style="text-align:center;padding:40px;color:#888;">
                <p style="font-size:3rem;">🔖</p>
                <p>No bookmarks yet</p>
                <p style="font-size:0.9rem;margin-top:10px;">Click "+ New Bookmark" to add one</p>
            </div>
        `;
        return;
    }
    
    // Group bookmarks by category
    const categories = {};
    currentBookmarks.forEach(bookmark => {
        const category = bookmark.category || 'General';
        if (!categories[category]) {
            categories[category] = [];
        }
        categories[category].push(bookmark);
    });
    
    let html = '';
    
    Object.keys(categories).forEach(category => {
        html += `<div class="bookmark-category">
            <h4 class="bookmark-category-title">${category}</h4>`;
        
        categories[category].forEach(bookmark => {
            html += `
                <div class="bookmark-item" onclick="openBookmark('${escapeHtml(bookmark.url)}')">
                    <div class="bookmark-icon">🔗</div>
                    <div class="bookmark-info">
                        <div class="bookmark-title">${escapeHtml(bookmark.title)}</div>
                        <div class="bookmark-url">${escapeHtml(truncateUrl(bookmark.url))}</div>
                        ${bookmark.description ? `<div class="bookmark-description">${escapeHtml(bookmark.description)}</div>` : ''}
                        ${bookmark.tags ? `<div class="bookmark-tags">${renderTags(bookmark.tags)}</div>` : ''}
                    </div>
                    <div class="bookmark-actions">
                        <button onclick="event.stopPropagation();editBookmarkForm(${bookmark.id})" class="btn-bookmark-edit" title="Edit">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                        </button>
                        <button onclick="event.stopPropagation();confirmDeleteBookmark(${bookmark.id})" class="btn-bookmark-delete" title="Delete">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"/>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
    });
    
    container.innerHTML = html;
}

function renderTags(tags) {
    if (!tags) return '';
    const tagArray = tags.split(',').map(t => t.trim()).filter(t => t);
    return tagArray.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('');
}

function truncateUrl(url) {
    if (url.length <= 50) return url;
    return url.substring(0, 47) + '...';
}

function openBookmark(url) {
    window.open(url, '_blank');
}

function showNewBookmarkForm() {
    console.log('Show new bookmark form');
    currentEditingBookmarkId = null;
    document.getElementById('bookmarkTitle').value = '';
    document.getElementById('bookmarkUrl').value = '';
    document.getElementById('bookmarkDescription').value = '';
    document.getElementById('bookmarkCategory').value = 'General';
    document.getElementById('bookmarkTags').value = '';
    document.getElementById('bookmarkFormTitle').textContent = 'New Bookmark';
    document.getElementById('bookmarkFormContainer').classList.remove('hidden');
    document.getElementById('bookmarksList').classList.add('hidden');
}

function editBookmarkForm(bookmarkId) {
    console.log('Edit bookmark:', bookmarkId);
    const bookmark = currentBookmarks.find(b => b.id === bookmarkId);
    if (!bookmark) return;
    
    currentEditingBookmarkId = bookmarkId;
    document.getElementById('bookmarkTitle').value = bookmark.title;
    document.getElementById('bookmarkUrl').value = bookmark.url;
    document.getElementById('bookmarkDescription').value = bookmark.description || '';
    document.getElementById('bookmarkCategory').value = bookmark.category || 'General';
    document.getElementById('bookmarkTags').value = bookmark.tags || '';
    document.getElementById('bookmarkFormTitle').textContent = 'Edit Bookmark';
    document.getElementById('bookmarkFormContainer').classList.remove('hidden');
    document.getElementById('bookmarksList').classList.add('hidden');
}

async function saveBookmark() {
    console.log('Save bookmark');
    const title = document.getElementById('bookmarkTitle').value.trim();
    const url = document.getElementById('bookmarkUrl').value.trim();
    const description = document.getElementById('bookmarkDescription').value.trim();
    const category = document.getElementById('bookmarkCategory').value;
    const tags = document.getElementById('bookmarkTags').value.trim();
    
    if (!title || !url) {
        if (typeof showToast === 'function') {
            showToast('Title and URL are required', 'error');
        } else {
            alert('Title and URL are required');
        }
        return;
    }
    
    // Validate URL format
    try {
        new URL(url);
    } catch (e) {
        if (typeof showToast === 'function') {
            showToast('Please enter a valid URL', 'error');
        } else {
            alert('Please enter a valid URL');
        }
        return;
    }
    
    try {
        const apiUrl = currentEditingBookmarkId ? `/bookmarks/${currentEditingBookmarkId}` : '/bookmarks';
        const method = currentEditingBookmarkId ? 'PUT' : 'POST';
        
        const response = await fetch(apiUrl, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, url, description, category, tags })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            if (typeof showToast === 'function') {
                showToast(currentEditingBookmarkId ? 'Bookmark updated!' : 'Bookmark created!', 'success');
            }
            cancelBookmarkEdit();
            await loadBookmarks();
        } else {
            throw new Error(data.error || 'Failed to save bookmark');
        }
    } catch (error) {
        console.error('Save error:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to save bookmark: ' + error.message, 'error');
        } else {
            alert('Failed to save bookmark: ' + error.message);
        }
    }
}

function cancelBookmarkEdit() {
    console.log('Cancel bookmark edit');
    currentEditingBookmarkId = null;
    document.getElementById('bookmarkFormContainer').classList.add('hidden');
    document.getElementById('bookmarksList').classList.remove('hidden');
}

function confirmDeleteBookmark(bookmarkId) {
    console.log('Confirm delete bookmark:', bookmarkId);
    const bookmark = currentBookmarks.find(b => b.id === bookmarkId);
    if (bookmark && confirm(`Delete "${bookmark.title}"?`)) {
        deleteBookmarkById(bookmarkId);
    }
}

async function deleteBookmarkById(bookmarkId) {
    console.log('Delete bookmark:', bookmarkId);
    try {
        const response = await fetch(`/bookmarks/${bookmarkId}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.status === 'success') {
            if (typeof showToast === 'function') {
                showToast('Bookmark deleted!', 'success');
            }
            await loadBookmarks();
        } else {
            throw new Error(data.error || 'Failed to delete bookmark');
        }
    } catch (error) {
        console.error('Delete error:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to delete bookmark: ' + error.message, 'error');
        } else {
            alert('Failed to delete bookmark: ' + error.message);
        }
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Expose functions globally for onclick handlers and app.js
window.setupBookmarksEventListeners = setupBookmarksEventListeners;
window.showNewBookmarkForm = showNewBookmarkForm;
window.saveBookmark = saveBookmark;
window.cancelBookmarkEdit = cancelBookmarkEdit;
window.editBookmarkForm = editBookmarkForm;
window.confirmDeleteBookmark = confirmDeleteBookmark;
window.openBookmark = openBookmark;
