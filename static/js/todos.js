// Todo Management
let currentTodos = [];
let todosListenersSetup = false;

console.log('Todos.js loaded');

// This function will be called by app.js when Todos panel opens
function setupTodosEventListeners() {
    console.log('Setting up todos listeners...');
    if (todosListenersSetup) {
        console.log('Todos listeners already set up, just reloading data...');
        loadTodos();
        return;
    }
    todosListenersSetup = true;
    loadTodos();
    
    // Quick add todo
    const quickAddInput = document.getElementById('quickAddTodo');
    const quickAddBtn = document.getElementById('quickAddBtn');
    
    if (quickAddBtn) {
        quickAddBtn.addEventListener('click', (e) => {
            e.preventDefault();
            quickAddTodo();
        });
    }
    
    if (quickAddInput) {
        quickAddInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                quickAddTodo();
            }
        });
    }
    
    // Clear completed button
    const clearCompletedBtn = document.getElementById('clearCompleted');
    if (clearCompletedBtn) {
        clearCompletedBtn.addEventListener('click', clearCompletedTodos);
    }
}

async function loadTodos() {
    try {
        const response = await fetch('/todos');
        const data = await response.json();
        
        if (data.status === 'success') {
            currentTodos = data.todos;
            renderTodos();
        }
    } catch (error) {
        console.error('Error loading todos:', error);
    }
}

function renderTodos() {
    const todoContainer = document.getElementById('todosList');
    if (!todoContainer) {
        console.error('todosList container not found');
        return;
    }
    
    const pendingTodos = currentTodos.filter(t => !t.completed);
    const completedTodos = currentTodos.filter(t => t.completed);
    
    if (currentTodos.length === 0) {
        todoContainer.innerHTML = `
            <div style="text-align:center;padding:40px;color:#888;">
                <p style="font-size:3rem;">📝</p>
                <p>No tasks yet</p>
                <p style="font-size:0.9rem;margin-top:10px;">Add your first task above!</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Pending todos
    if (pendingTodos.length > 0) {
        html += '<div class="todo-section"><h4>📋 To Do</h4>';
        html += pendingTodos.map(todo => renderTodoItem(todo)).join('');
        html += '</div>';
    }
    
    // Completed todos
    if (completedTodos.length > 0) {
        html += '<div class="todo-section completed-section"><h4>✅ Completed</h4>';
        html += completedTodos.map(todo => renderTodoItem(todo)).join('');
        html += '</div>';
    }
    
    todoContainer.innerHTML = html;
    updateTodoStats();
}

function renderTodoItem(todo) {
    const priorityColors = {
        'High': 'priority-high',
        'Medium': 'priority-medium',
        'Low': 'priority-low'
    };
    
    return `
        <div class="todo-item ${todo.completed ? 'completed' : ''}" data-todo-id="${todo.id}">
            <div class="todo-checkbox" onclick="toggleTodo(${todo.id})">
                ${todo.completed ? '✓' : ''}
            </div>
            <div class="todo-content">
                <span class="todo-task">${escapeHtml(todo.task)}</span>
                <div class="todo-meta">
                    <span class="todo-priority ${priorityColors[todo.priority]}">${todo.priority}</span>
                    ${todo.due_date ? `<span class="todo-due">📅 ${formatDate(todo.due_date)}</span>` : ''}
                </div>
            </div>
            <button class="todo-delete" onclick="deleteTodo(event, ${todo.id})" title="Delete">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
            </button>
        </div>
    `;
}

async function quickAddTodo() {
    const input = document.getElementById('quickAddTodo');
    const task = input.value.trim();
    
    if (!task) {
        return;
    }
    
    try {
        const response = await fetch('/todos', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ task, priority: 'Medium' })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            input.value = '';
            if (typeof showToast === 'function') {
                showToast('Task added!', 'success');
            }
            await loadTodos();
        } else {
            if (typeof showToast === 'function') {
                showToast('Error adding task: ' + data.error, 'error');
            } else {
                alert('Error adding todo: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Error adding todo:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to add task', 'error');
        } else {
            alert('Failed to add todo');
        }
    }
}

async function toggleTodo(todoId) {
    try {
        const response = await fetch(`/todos/${todoId}/toggle`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            await loadTodos();
        } else {
            if (typeof showToast === 'function') {
                showToast('Error toggling task', 'error');
            }
        }
    } catch (error) {
        console.error('Error toggling todo:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to toggle task', 'error');
        }
    }
}

async function deleteTodo(event, todoId) {
    event.stopPropagation();
    
    if (!confirm('Delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`/todos/${todoId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            if (typeof showToast === 'function') {
                showToast('Task deleted!', 'success');
            }
            await loadTodos();
        } else {
            if (typeof showToast === 'function') {
                showToast('Error deleting task: ' + data.error, 'error');
            } else {
                alert('Error deleting todo: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Error deleting todo:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to delete task', 'error');
        } else {
            alert('Failed to delete todo');
        }
    }
}

async function clearCompletedTodos() {
    const completedCount = currentTodos.filter(t => t.completed).length;
    
    if (completedCount === 0) {
        if (typeof showToast === 'function') {
            showToast('No completed tasks to clear', 'info');
        } else {
            alert('No completed tasks to clear');
        }
        return;
    }
    
    if (!confirm(`Delete ${completedCount} completed task(s)?`)) {
        return;
    }
    
    try {
        const response = await fetch('/todos/completed', {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            if (typeof showToast === 'function') {
                showToast(data.message || 'Completed tasks cleared!', 'success');
            }
            await loadTodos();
        } else {
            if (typeof showToast === 'function') {
                showToast('Error clearing tasks', 'error');
            }
        }
    } catch (error) {
        console.error('Error clearing completed todos:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to clear completed tasks', 'error');
        } else {
            alert('Failed to clear completed tasks');
        }
    }
}

function updateTodoStats() {
    const statsContainer = document.getElementById('todoStats');
    if (!statsContainer) return;
    
    const total = currentTodos.length;
    const completed = currentTodos.filter(t => t.completed).length;
    const pending = total - completed;
    
    statsContainer.innerHTML = `
        <span>${total} total</span>
        <span>•</span>
        <span>${pending} pending</span>
        <span>•</span>
        <span>${completed} done</span>
    `;
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
        return 'Tomorrow';
    } else {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
}

// Expose functions globally for onclick handlers and app.js
window.setupTodosEventListeners = setupTodosEventListeners;
window.quickAddTodo = quickAddTodo;
window.toggleTodo = toggleTodo;
window.deleteTodo = deleteTodo;
window.clearCompletedTodos = clearCompletedTodos;
