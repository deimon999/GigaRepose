// Todo Management
let currentTodos = [];

// Initialize todos when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadTodos();
    setupTodoEventListeners();
});

function setupTodoEventListeners() {
    // Toggle todo panel
    const todosToggle = document.getElementById('todosToggle');
    if (todosToggle) {
        todosToggle.addEventListener('click', (e) => {
            e.preventDefault();
            const todoPanel = document.getElementById('todoPanel');
            todoPanel.classList.toggle('active');
        });
    }
    
    // Quick add todo
    const quickAddInput = document.getElementById('quickAddTodo');
    const quickAddBtn = document.getElementById('quickAddBtn');
    
    if (quickAddBtn) {
        quickAddBtn.addEventListener('click', quickAddTodo);
    }
    
    if (quickAddInput) {
        quickAddInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
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
    const todoContainer = document.getElementById('todoList');
    if (!todoContainer) return;
    
    const pendingTodos = currentTodos.filter(t => !t.completed);
    const completedTodos = currentTodos.filter(t => t.completed);
    
    if (currentTodos.length === 0) {
        todoContainer.innerHTML = `
            <div class="empty-todos">
                <p>✅ No tasks yet</p>
                <p>Add your first task above!</p>
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
            loadTodos();
        } else {
            alert('Error adding todo: ' + data.error);
        }
    } catch (error) {
        console.error('Error adding todo:', error);
        alert('Failed to add todo');
    }
}

async function toggleTodo(todoId) {
    try {
        const response = await fetch(`/todos/${todoId}/toggle`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            loadTodos();
        }
    } catch (error) {
        console.error('Error toggling todo:', error);
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
            loadTodos();
        } else {
            alert('Error deleting todo: ' + data.error);
        }
    } catch (error) {
        console.error('Error deleting todo:', error);
        alert('Failed to delete todo');
    }
}

async function clearCompletedTodos() {
    const completedCount = currentTodos.filter(t => t.completed).length;
    
    if (completedCount === 0) {
        alert('No completed tasks to clear');
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
            loadTodos();
            console.log('✓', data.message);
        }
    } catch (error) {
        console.error('Error clearing completed todos:', error);
        alert('Failed to clear completed tasks');
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
