// Chat state
let conversationHistory = [];

// DOM elements
const messageInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');

// Send message on Enter
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
});

// Send button click
sendButton.addEventListener('click', sendMessage);

function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Clear welcome message if it exists
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Add user message to UI
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    
    // Disable send button
    sendButton.disabled = true;
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to backend
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            history: conversationHistory,
            chat_id: window.currentChatId || null
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove typing indicator
        removeTypingIndicator();
        
        // Store chat_id if returned
        if (data.chat_id) {
            window.currentChatId = data.chat_id;
        }
        
        // Add assistant response
        if (data.response) {
            addMessage(data.response, 'assistant');
            
            // Update conversation history
            conversationHistory.push(
                { role: 'user', content: message },
                { role: 'assistant', content: data.response }
            );
        } else if (data.error) {
            addMessage('Sorry, I encountered an error: ' + data.error, 'assistant');
        }
        
        // Re-enable send button
        sendButton.disabled = false;
        messageInput.focus();
    })
    .catch(error => {
        removeTypingIndicator();
        addMessage('Sorry, I could not connect to the server. Please make sure the backend is running.', 'assistant');
        sendButton.disabled = false;
        messageInput.focus();
        console.error('Error:', error);
    });
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? 'U' : 'J';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    // Convert newlines to <br> tags for proper formatting
    const formattedText = text.replace(/\n/g, '<br>');
    content.innerHTML = formattedText;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Capture assistant messages for summary/flashcard features
    if (sender === 'assistant') {
        captureLastMessage(text);
    }
}

function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'message assistant typing-indicator-message';
    indicator.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'J';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
    
    content.appendChild(typingDiv);
    indicator.appendChild(avatar);
    indicator.appendChild(content);
    
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// Summary and Flashcard features
let lastAssistantMessage = '';

// Capture last assistant message
function captureLastMessage(text) {
    lastAssistantMessage = text;
}

document.getElementById('summarizeBtn').addEventListener('click', async () => {
    if (!lastAssistantMessage) {
        alert('No message to summarize. Chat with Nexus first!');
        return;
    }
    
    try {
        const response = await fetch('/summarize', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: lastAssistantMessage})
        });
        
        const data = await response.json();
        if (data.summary) {
            addMessage(`📝 Summary:\n\n${data.summary}`, 'assistant');
        }
    } catch (error) {
        console.error('Summarize error:', error);
        alert('Failed to generate summary');
    }
});

document.getElementById('flashcardsBtn').addEventListener('click', async () => {
    if (!lastAssistantMessage) {
        alert('No message to create flashcards from. Chat with Nexus first!');
        return;
    }
    
    try {
        const response = await fetch('/generate-flashcards', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: lastAssistantMessage, num_cards: 5})
        });
        
        const data = await response.json();
        if (data.flashcards && data.flashcards.length > 0) {
            let flashcardsHTML = '🎴 **Flashcards Generated:**\n\n';
            data.flashcards.forEach((card, index) => {
                flashcardsHTML += `**Card ${index + 1}:**\nQ: ${card.question}\nA: ${card.answer}\n\n`;
            });
            addMessage(flashcardsHTML, 'assistant');
        }
    } catch (error) {
        console.error('Flashcards error:', error);
        alert('Failed to generate flashcards');
    }
});

// Explain button - Generate detailed explanation
document.getElementById('explainBtn').addEventListener('click', () => {
    const modal = document.getElementById('explainModal');
    const input = document.getElementById('explainTopicInput');
    
    modal.classList.remove('hidden');
    input.value = '';
    input.focus();
});

// Explain topic input - Submit on Enter key
document.getElementById('explainTopicInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('explainConfirmBtn').click();
    }
});

// Explain modal - Cancel button
document.getElementById('explainCancelBtn').addEventListener('click', () => {
    document.getElementById('explainModal').classList.add('hidden');
});

// Explain modal - Confirm button
document.getElementById('explainConfirmBtn').addEventListener('click', async () => {
    const topic = document.getElementById('explainTopicInput').value.trim();
    const modal = document.getElementById('explainModal');
    
    if (!topic) {
        if (typeof showToast === 'function') {
            showToast('Please enter a topic to explain', 'error');
        }
        return;
    }
    
    modal.classList.add('hidden');
    
    // Show loading message
    addMessage(`� Generating detailed explanation for: "${topic}"...`, 'assistant');
    
    try {
        const response = await fetch('/explain', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({topic: topic.trim()})
        });
        
        const data = await response.json();
        if (data.explanation) {
            let explanationHTML = `📚 **Detailed Explanation: ${topic}**\n\n`;
            explanationHTML += data.explanation;
            
            if (data.context_found) {
                explanationHTML += `\n\n---\n📖 *Based on ${data.sources} reference document(s) from your uploaded materials*`;
            }
            
            addMessage(explanationHTML, 'assistant');
        } else if (data.error) {
            addMessage(`❌ Error: ${data.error}`, 'assistant');
        }
    } catch (error) {
        console.error('Explain error:', error);
        addMessage('❌ Failed to generate explanation. Please try again.', 'assistant');
    }
});

// Explain modal - Enter key support
document.getElementById('explainTopicInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('explainConfirmBtn').click();
    }
});

// Navigation functionality
let isNavigating = false;

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Prevent rapid clicks
        if (isNavigating) {
            return;
        }
        isNavigating = true;
        
        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        
        // Add active class to clicked item
        item.classList.add('active');
        
        // Close all panels first
        document.querySelectorAll('.documents-panel, .notes-panel, .todo-panel, .pomodoro-panel, .bookmarks-panel, .chat-history-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        // Small delay to allow transition
        setTimeout(() => {
            // Get the view type
            const view = item.getAttribute('data-view');
            
            // Open corresponding panel
            if (view === 'documents') {
                document.getElementById('documentsPanel').classList.add('active');
                // Ensure documents event listeners are set up when panel opens
                if (typeof window.setupDocumentsEventListeners === 'function') {
                    window.setupDocumentsEventListeners();
                }
            } else if (view === 'notes') {
                document.getElementById('notesPanel').classList.add('active');
                // Ensure notes event listeners are set up when panel opens
                if (typeof window.setupNotesEventListeners === 'function') {
                    window.setupNotesEventListeners();
                }
            } else if (view === 'todos') {
                document.getElementById('todoPanel').classList.add('active');
                // Ensure todos event listeners are set up when panel opens
                if (typeof window.setupTodosEventListeners === 'function') {
                    window.setupTodosEventListeners();
                }
            } else if (view === 'pomodoro') {
                document.getElementById('pomodoroPanel').classList.add('active');
                // Ensure pomodoro event listeners are set up when panel opens
                if (typeof window.setupPomodoroEventListeners === 'function') {
                    window.setupPomodoroEventListeners();
                }
            } else if (view === 'bookmarks') {
                document.getElementById('bookmarksPanel').classList.add('active');
                // Ensure bookmarks event listeners are set up when panel opens
                if (typeof window.setupBookmarksEventListeners === 'function') {
                    window.setupBookmarksEventListeners();
                }
            } else if (view === 'game') {
                document.getElementById('gamePanel').classList.add('active');
                // Initialize game when panel opens
                if (typeof initGame === 'function') {
                    initGame();
                }
            } else if (view === 'chat-history') {
                document.getElementById('chatHistoryPanel').classList.add('active');
                // Ensure chat history event listeners are set up when panel opens
                if (typeof window.setupChatHistoryEventListeners === 'function') {
                    window.setupChatHistoryEventListeners();
                }
            }
            // 'chat' view just shows the main chat area (no panel)
            
            // Reset navigation lock after transition
            setTimeout(() => {
                isNavigating = false;
            }, 100);
        }, 50);
    });
});

// Close panel functionality
function closePanel() {
    document.querySelectorAll('.documents-panel, .notes-panel, .todo-panel, .pomodoro-panel, .bookmarks-panel, .chat-history-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Set Home nav as active
    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
    document.querySelector('.nav-item[data-view="chat"]').classList.add('active');
}

// Add close panel listeners
document.querySelectorAll('.close-btn').forEach(btn => {
    btn.addEventListener('click', closePanel);
});

// Close all panels on page load and set Home as active
window.addEventListener('load', () => {
    // Close all panels
    document.querySelectorAll('.documents-panel, .notes-panel, .todo-panel, .pomodoro-panel, .bookmarks-panel, .chat-history-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Set Home nav as active
    document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
    const homeNav = document.querySelector('.nav-item[data-view="chat"]');
    if (homeNav) {
        homeNav.classList.add('active');
    }
    
    // Focus input
    messageInput.focus();
});
