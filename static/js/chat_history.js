// Chat History Management
let currentChatId = null;
let chatHistoryListenersSetup = false;

// Load chat history list
async function loadChatHistory() {
    try {
        const response = await fetch('/chat-history');
        const data = await response.json();
        
        const historyList = document.getElementById('chatHistoryList');
        if (!historyList) return;
        
        if (!data.chats || data.chats.length === 0) {
            historyList.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:40px;">No chat history yet<br><small>Start a conversation to see it here</small></p>';
            return;
        }
        
        historyList.innerHTML = '';
        
        data.chats.forEach(chat => {
            const chatItem = createChatHistoryItem(chat);
            historyList.appendChild(chatItem);
        });
    } catch (error) {
        console.error('Error loading chat history:', error);
        const historyList = document.getElementById('chatHistoryList');
        if (historyList) {
            historyList.innerHTML = '<p style="text-align:center;color:#ef4444;">Error loading chat history</p>';
        }
    }
}

// Create chat history item element
function createChatHistoryItem(chat) {
    const item = document.createElement('div');
    item.className = 'chat-history-item';
    item.dataset.chatId = chat.id;
    
    const updatedDate = chat.updated_at ? new Date(chat.updated_at).toLocaleString() : '';
    const messagePreview = chat.first_message ? (chat.first_message.substring(0, 60) + (chat.first_message.length > 60 ? '...' : '')) : 'No messages';
    
    item.innerHTML = `
        <div class="chat-history-icon">💬</div>
        <div class="chat-history-info">
            <div class="chat-history-title">${escapeHtml(chat.title)}</div>
            <div class="chat-history-preview">${escapeHtml(messagePreview)}</div>
            <div class="chat-history-meta">
                <span>${chat.message_count || 0} messages</span>
                <span>•</span>
                <span>${updatedDate}</span>
            </div>
        </div>
        <div class="chat-history-actions">
            <button onclick="loadChatConversation(${chat.id})" class="load-chat-btn" title="Load this conversation">
                📂
            </button>
            <button onclick="deleteChatHistory(${chat.id}, '${escapeHtml(chat.title)}')" class="delete-btn" title="Delete">
                🗑️
            </button>
        </div>
    `;
    
    // Click to load chat
    item.addEventListener('click', (e) => {
        if (!e.target.classList.contains('delete-btn') && !e.target.classList.contains('load-chat-btn')) {
            loadChatConversation(chat.id);
        }
    });
    
    return item;
}

// Load a specific chat conversation
async function loadChatConversation(chatId) {
    try {
        const response = await fetch(`/chat-history/${chatId}`);
        const data = await response.json();
        
        if (!data.messages) {
            showToast('Chat not found', 'error');
            return;
        }
        
        // Clear current chat
        const messagesContainer = document.getElementById('messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
        
        // Load messages into chat
        data.messages.forEach(msg => {
            if (messagesContainer) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.role}`;
                messageDiv.innerHTML = `
                    <div class="message-content">
                        <div class="message-text">${formatMessage(msg.content)}</div>
                        <div class="message-time">${new Date(msg.timestamp).toLocaleTimeString()}</div>
                    </div>
                `;
                messagesContainer.appendChild(messageDiv);
            }
        });
        
        // Scroll to bottom
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        // Set current chat ID
        currentChatId = chatId;
        
        // Close history panel
        closePanel();
        
        showToast(`Loaded: ${data.chat.title}`, 'success');
    } catch (error) {
        console.error('Error loading chat conversation:', error);
        showToast('Failed to load conversation', 'error');
    }
}

// Delete chat from history
async function deleteChatHistory(chatId, title) {
    if (!confirm(`Delete chat "${title}"?`)) return;
    
    try {
        const response = await fetch(`/chat-history/${chatId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Chat deleted', 'success');
            loadChatHistory();
            
            // If this was the current chat, reset
            if (currentChatId === chatId) {
                currentChatId = null;
                const messagesContainer = document.getElementById('messages');
                if (messagesContainer) {
                    messagesContainer.innerHTML = '';
                }
            }
        } else {
            showToast(data.error || 'Delete failed', 'error');
        }
    } catch (error) {
        console.error('Error deleting chat:', error);
        showToast('Error deleting chat', 'error');
    }
}

// Clear all chat history
async function clearAllChatHistory() {
    showModal({
        title: 'Clear All Chat History?',
        message: 'This will permanently delete all your chat conversations. This action cannot be undone.',
        icon: '⚠️',
        confirmText: 'Clear All',
        cancelText: 'Cancel',
        onConfirm: async () => {
            try {
                const response = await fetch('/chat-history/clear', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showToast('All chat history cleared', 'success');
                    loadChatHistory();
                    currentChatId = null;
                    
                    // Clear current chat display
                    const messagesContainer = document.getElementById('messages');
                    if (messagesContainer) {
                        messagesContainer.innerHTML = '';
                    }
                } else {
                    showToast(data.error || 'Failed to clear history', 'error');
                }
            } catch (error) {
                console.error('Error clearing chat history:', error);
                showToast('Error clearing history', 'error');
            }
        }
    });
}

// Start new chat
function startNewChat() {
    currentChatId = null;
    const messagesContainer = document.getElementById('messages');
    if (messagesContainer) {
        messagesContainer.innerHTML = '';
    }
    closePanel();
    showToast('New chat started', 'info');
}

// Search chat history
async function searchChatHistory() {
    const searchInput = document.getElementById('searchChatHistory');
    if (!searchInput) return;
    
    const query = searchInput.value.trim();
    
    if (!query) {
        loadChatHistory(); // Show all if empty
        return;
    }
    
    try {
        const response = await fetch('/chat-history/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        const historyList = document.getElementById('chatHistoryList');
        if (!historyList) return;
        
        if (!data.results || data.results.length === 0) {
            historyList.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:40px;">No results found</p>';
            return;
        }
        
        historyList.innerHTML = '';
        
        // Group results by chat
        const chatMap = new Map();
        data.results.forEach(msg => {
            if (!chatMap.has(msg.chat_id)) {
                chatMap.set(msg.chat_id, {
                    id: msg.chat_id,
                    title: msg.chat_title,
                    messages: []
                });
            }
            chatMap.get(msg.chat_id).messages.push(msg);
        });
        
        // Display results
        chatMap.forEach(chat => {
            const item = document.createElement('div');
            item.className = 'chat-history-item';
            item.innerHTML = `
                <div class="chat-history-icon">🔍</div>
                <div class="chat-history-info">
                    <div class="chat-history-title">${escapeHtml(chat.title)}</div>
                    <div class="chat-history-preview">${chat.messages.length} matching message(s)</div>
                </div>
                <button onclick="loadChatConversation(${chat.id})" class="load-chat-btn">Load</button>
            `;
            historyList.appendChild(item);
        });
    } catch (error) {
        console.error('Error searching chat history:', error);
        showToast('Error searching', 'error');
    }
}

// Setup function called when chat history panel opens
function setupChatHistoryEventListeners() {
    console.log('Setting up chat history listeners...');
    
    // Always reload chat history when panel opens
    loadChatHistory();
    
    // Only set up event listeners once
    if (chatHistoryListenersSetup) {
        console.log('Chat history listeners already set up, just reloaded data');
        return;
    }
    chatHistoryListenersSetup = true;
    
    // Setup search input
    const searchInput = document.getElementById('searchChatHistory');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchChatHistory, 300));
    }
}

// Utility: debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Utility: escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Utility: format message text
function formatMessage(text) {
    return text.replace(/\n/g, '<br>');
}

// Export to global scope
window.setupChatHistoryEventListeners = setupChatHistoryEventListeners;
window.loadChatHistory = loadChatHistory;
window.loadChatConversation = loadChatConversation;
window.deleteChatHistory = deleteChatHistory;
window.clearAllChatHistory = clearAllChatHistory;
window.startNewChat = startNewChat;
window.currentChatId = currentChatId;
