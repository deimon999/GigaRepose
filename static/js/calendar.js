// Calendar Management
let currentEvents = [];
let currentEditingEventId = null;
let currentViewDate = new Date();

// Initialize calendar when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadEvents();
    setupCalendarEventListeners();
    renderCalendar();
});

function setupCalendarEventListeners() {
    // Toggle calendar panel
    const calendarToggle = document.getElementById('calendarToggle');
    if (calendarToggle) {
        calendarToggle.addEventListener('click', toggleCalendarPanel);
    }
    
    // New event button
    const newEventBtn = document.getElementById('newEventBtn');
    if (newEventBtn) {
        newEventBtn.addEventListener('click', showNewEventForm);
    }
    
    // Save event button
    const saveEventBtn = document.getElementById('saveEventBtn');
    if (saveEventBtn) {
        saveEventBtn.addEventListener('click', saveEvent);
    }
    
    // Cancel event button
    const cancelEventBtn = document.getElementById('cancelEventBtn');
    if (cancelEventBtn) {
        cancelEventBtn.addEventListener('click', cancelEventEdit);
    }
    
    // Calendar navigation
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    const todayBtn = document.getElementById('todayBtn');
    
    if (prevMonthBtn) prevMonthBtn.addEventListener('click', () => changeMonth(-1));
    if (nextMonthBtn) nextMonthBtn.addEventListener('click', () => changeMonth(1));
    if (todayBtn) todayBtn.addEventListener('click', goToToday);
}

function toggleCalendarPanel() {
    const calendarPanel = document.getElementById('calendarPanel');
    if (calendarPanel) {
        calendarPanel.classList.toggle('hidden');
        if (!calendarPanel.classList.contains('hidden')) {
            loadEvents();
            renderCalendar();
        }
    }
}

async function loadEvents() {
    try {
        const response = await fetch('/events');
        const data = await response.json();
        
        if (data.status === 'success') {
            currentEvents = data.events;
            renderUpcomingEvents();
        }
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

function renderCalendar() {
    const year = currentViewDate.getFullYear();
    const month = currentViewDate.getMonth();
    
    // Update month display
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
    document.getElementById('currentMonth').textContent = `${monthNames[month]} ${year}`;
    
    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    const calendarGrid = document.getElementById('calendarGrid');
    calendarGrid.innerHTML = '';
    
    // Add empty cells for days before month starts
    for (let i = 0; i < firstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day empty';
        calendarGrid.appendChild(emptyDay);
    }
    
    // Add days of month
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
        const dayCell = document.createElement('div');
        dayCell.className = 'calendar-day';
        
        const currentDate = new Date(year, month, day);
        const dateStr = formatDateForAPI(currentDate);
        
        // Check if today
        if (currentDate.toDateString() === today.toDateString()) {
            dayCell.classList.add('today');
        }
        
        // Check if has events
        const dayEvents = currentEvents.filter(e => e.event_date === dateStr);
        if (dayEvents.length > 0) {
            dayCell.classList.add('has-events');
        }
        
        dayCell.innerHTML = `
            <span class="day-number">${day}</span>
            ${dayEvents.length > 0 ? `<span class="event-count">${dayEvents.length}</span>` : ''}
        `;
        
        dayCell.addEventListener('click', () => showDayEvents(currentDate));
        calendarGrid.appendChild(dayCell);
    }
}

function renderUpcomingEvents() {
    const upcomingContainer = document.getElementById('upcomingEvents');
    if (!upcomingContainer) return;
    
    const today = new Date();
    const upcoming = currentEvents.filter(e => {
        const eventDate = new Date(e.event_date);
        return eventDate >= today;
    }).slice(0, 5);
    
    if (upcoming.length === 0) {
        upcomingContainer.innerHTML = '<p class="empty-message">No upcoming events</p>';
        return;
    }
    
    upcomingContainer.innerHTML = upcoming.map(event => `
        <div class="event-item ${event.completed ? 'completed' : ''}" onclick="editEvent(${event.id})">
            <div class="event-info">
                <h4>${escapeHtml(event.title)}</h4>
                <p class="event-meta">
                    📅 ${formatDate(event.event_date)}
                    ${event.event_time ? `⏰ ${event.event_time}` : ''}
                    ${event.duration ? `⏱️ ${event.duration}min` : ''}
                </p>
                <span class="event-category">${event.category}</span>
            </div>
            <button class="event-check" onclick="toggleEventComplete(event, ${event.id})" title="${event.completed ? 'Mark incomplete' : 'Mark complete'}">
                ${event.completed ? '✓' : '○'}
            </button>
        </div>
    `).join('');
}

function showDayEvents(date) {
    const dateStr = formatDateForAPI(date);
    const dayEvents = currentEvents.filter(e => e.event_date === dateStr);
    
    if (dayEvents.length === 0) {
        // No events, create new one
        showNewEventForm(dateStr);
        return;
    }
    
    // Show events for that day
    alert(`Events on ${formatDate(dateStr)}:\n\n` + 
          dayEvents.map(e => `• ${e.title} ${e.event_time ? 'at ' + e.event_time : ''}`).join('\n'));
}

function showNewEventForm(prefillDate = null) {
    currentEditingEventId = null;
    document.getElementById('eventTitle').value = '';
    document.getElementById('eventDescription').value = '';
    document.getElementById('eventDate').value = prefillDate || formatDateForAPI(new Date());
    document.getElementById('eventTime').value = '';
    document.getElementById('eventDuration').value = '60';
    document.getElementById('eventCategory').value = 'Study';
    
    document.getElementById('eventFormContainer').classList.remove('hidden');
    document.getElementById('upcomingEvents').classList.add('hidden');
    document.getElementById('calendarView').classList.add('hidden');
    document.getElementById('eventFormTitle').textContent = 'New Event';
}

async function editEvent(eventId) {
    try {
        const response = await fetch(`/events/${eventId}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            currentEditingEventId = eventId;
            document.getElementById('eventTitle').value = data.event.title;
            document.getElementById('eventDescription').value = data.event.description || '';
            document.getElementById('eventDate').value = data.event.event_date;
            document.getElementById('eventTime').value = data.event.event_time || '';
            document.getElementById('eventDuration').value = data.event.duration;
            document.getElementById('eventCategory').value = data.event.category;
            
            document.getElementById('eventFormContainer').classList.remove('hidden');
            document.getElementById('upcomingEvents').classList.add('hidden');
            document.getElementById('calendarView').classList.add('hidden');
            document.getElementById('eventFormTitle').textContent = 'Edit Event';
        }
    } catch (error) {
        console.error('Error loading event:', error);
        alert('Failed to load event');
    }
}

async function saveEvent() {
    const title = document.getElementById('eventTitle').value.trim() || 'Untitled Event';
    const description = document.getElementById('eventDescription').value.trim();
    const eventDate = document.getElementById('eventDate').value;
    const eventTime = document.getElementById('eventTime').value;
    const duration = parseInt(document.getElementById('eventDuration').value) || 60;
    const category = document.getElementById('eventCategory').value;
    
    if (!eventDate) {
        alert('Event date is required');
        return;
    }
    
    try {
        let response;
        
        if (currentEditingEventId) {
            // Update existing event
            response = await fetch(`/events/${currentEditingEventId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ title, description, event_date: eventDate, event_time: eventTime, duration, category })
            });
        } else {
            // Create new event
            response = await fetch('/events', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ title, description, event_date: eventDate, event_time: eventTime, duration, category })
            });
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            cancelEventEdit();
            loadEvents();
            console.log('✓', data.message);
        } else {
            alert('Error saving event: ' + data.error);
        }
    } catch (error) {
        console.error('Error saving event:', error);
        alert('Failed to save event');
    }
}

async function toggleEventComplete(event, eventId) {
    event.stopPropagation();
    
    try {
        const response = await fetch(`/events/${eventId}/toggle`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            loadEvents();
        }
    } catch (error) {
        console.error('Error toggling event:', error);
    }
}

function cancelEventEdit() {
    currentEditingEventId = null;
    document.getElementById('eventFormContainer').classList.add('hidden');
    document.getElementById('upcomingEvents').classList.remove('hidden');
    document.getElementById('calendarView').classList.remove('hidden');
}

function changeMonth(delta) {
    currentViewDate.setMonth(currentViewDate.getMonth() + delta);
    renderCalendar();
}

function goToToday() {
    currentViewDate = new Date();
    renderCalendar();
}

// Utility functions
function formatDateForAPI(date) {
    return date.toISOString().split('T')[0];
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
