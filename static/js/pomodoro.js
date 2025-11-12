// Pomodoro Timer Management
let pomodoroTimer = null;
let pomodoroSeconds = 0;
let pomodoroRunning = false;
let currentSessionId = null;
let currentSessionType = 'work'; // 'work' or 'break'
let todayStats = { sessions: 0, minutes: 0 };
let pomodoroListenersSetup = false;

const WORK_DURATION = 25 * 60; // 25 minutes in seconds
const SHORT_BREAK = 5 * 60; // 5 minutes in seconds
const LONG_BREAK = 15 * 60; // 15 minutes in seconds

console.log('Pomodoro.js loaded');

// This function will be called by app.js when Pomodoro panel opens
function setupPomodoroEventListeners() {
    console.log('Setting up pomodoro listeners...');
    if (pomodoroListenersSetup) {
        console.log('Pomodoro listeners already set up, just reloading stats...');
        loadPomodoroStats();
        return;
    }
    pomodoroListenersSetup = true;
    loadPomodoroStats();
    
    // Start button
    const startBtn = document.getElementById('pomodoroStartBtn');
    if (startBtn) {
        startBtn.addEventListener('click', startPomodoro);
    }
    
    // Pause button
    const pauseBtn = document.getElementById('pomodoroPauseBtn');
    if (pauseBtn) {
        pauseBtn.addEventListener('click', pausePomodoro);
    }
    
    // Reset button
    const resetBtn = document.getElementById('pomodoroResetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetPomodoro);
    }
    
    // Skip button
    const skipBtn = document.getElementById('pomodoroSkipBtn');
    if (skipBtn) {
        skipBtn.addEventListener('click', skipToBreak);
    }
}

async function loadPomodoroStats() {
    try {
        const response = await fetch('/pomodoro/stats');
        const data = await response.json();
        
        if (data.status === 'success') {
            todayStats = data.stats;
            updateStatsDisplay();
        }
    } catch (error) {
        console.error('Error loading pomodoro stats:', error);
    }
}

function updateStatsDisplay() {
    const statsContainer = document.getElementById('pomodoroStats');
    if (!statsContainer) return;
    
    statsContainer.innerHTML = `
        <div class="stat-item">
            <div class="stat-value">${todayStats.sessions}</div>
            <div class="stat-label">Sessions</div>
        </div>
        <div class="stat-divider">•</div>
        <div class="stat-item">
            <div class="stat-value">${todayStats.minutes}</div>
            <div class="stat-label">Minutes</div>
        </div>
    `;
}

async function startPomodoro() {
    if (pomodoroRunning) return;
    
    try {
        // If starting fresh, create a session
        if (!currentSessionId && pomodoroSeconds === 0) {
            const taskName = document.getElementById('pomodoroTaskInput')?.value.trim() || 'Focus Session';
            
            const response = await fetch('/pomodoro/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    task_name: taskName,
                    duration: 25,
                    session_type: currentSessionType
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                currentSessionId = data.session_id;
                pomodoroSeconds = WORK_DURATION;
            }
        }
        
        pomodoroRunning = true;
        updatePomodoroButtons();
        
        pomodoroTimer = setInterval(() => {
            pomodoroSeconds--;
            updateTimerDisplay();
            
            if (pomodoroSeconds <= 0) {
                completePomodoro();
            }
        }, 1000);
        
    } catch (error) {
        console.error('Error starting pomodoro:', error);
        if (typeof showToast === 'function') {
            showToast('Failed to start session', 'error');
        }
    }
}

function pausePomodoro() {
    if (!pomodoroRunning) return;
    
    pomodoroRunning = false;
    clearInterval(pomodoroTimer);
    updatePomodoroButtons();
    
    if (typeof showToast === 'function') {
        showToast('Session paused', 'info');
    }
}

function resetPomodoro() {
    pomodoroRunning = false;
    clearInterval(pomodoroTimer);
    pomodoroSeconds = 0;
    currentSessionId = null;
    currentSessionType = 'work';
    
    updateTimerDisplay();
    updatePomodoroButtons();
    
    const taskInput = document.getElementById('pomodoroTaskInput');
    if (taskInput) taskInput.value = '';
}

async function completePomodoro() {
    pomodoroRunning = false;
    clearInterval(pomodoroTimer);
    
    try {
        if (currentSessionId && currentSessionType === 'work') {
            const response = await fetch(`/pomodoro/complete/${currentSessionId}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                // Play completion sound (optional)
                playCompletionSound();
                
                // Show notification
                if (typeof showToast === 'function') {
                    showToast('🎉 Pomodoro completed! Time for a break!', 'success');
                }
                
                // Update stats
                await loadPomodoroStats();
                
                // Ask if user wants to take a break
                if (confirm('Pomodoro completed! Take a 5-minute break?')) {
                    startBreak();
                } else {
                    resetPomodoro();
                }
            }
        } else if (currentSessionType === 'break') {
            if (typeof showToast === 'function') {
                showToast('Break finished! Ready to focus?', 'success');
            }
            resetPomodoro();
        }
    } catch (error) {
        console.error('Error completing pomodoro:', error);
    }
}

function startBreak() {
    currentSessionType = 'break';
    currentSessionId = null;
    pomodoroSeconds = SHORT_BREAK;
    
    updateTimerDisplay();
    updateSessionTypeDisplay();
    
    // Auto-start the break timer
    pomodoroRunning = true;
    updatePomodoroButtons();
    
    pomodoroTimer = setInterval(() => {
        pomodoroSeconds--;
        updateTimerDisplay();
        
        if (pomodoroSeconds <= 0) {
            completePomodoro();
        }
    }, 1000);
}

function skipToBreak() {
    if (currentSessionType === 'work') {
        pausePomodoro();
        if (confirm('Skip to break without completing this session?')) {
            resetPomodoro();
            startBreak();
        } else if (!pomodoroRunning) {
            startPomodoro();
        }
    }
}

function updateTimerDisplay() {
    const display = document.getElementById('pomodoroTimerDisplay');
    if (!display) return;
    
    const minutes = Math.floor(pomodoroSeconds / 60);
    const seconds = pomodoroSeconds % 60;
    
    display.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    
    // Update progress circle
    updateProgressCircle();
}

function updateProgressCircle() {
    const circle = document.getElementById('pomodoroProgressCircle');
    if (!circle) return;
    
    const totalSeconds = currentSessionType === 'work' ? WORK_DURATION : SHORT_BREAK;
    const percentage = ((totalSeconds - pomodoroSeconds) / totalSeconds) * 100;
    
    // SVG circle has circumference, calculate offset
    const circumference = 2 * Math.PI * 90; // radius = 90
    const offset = circumference - (percentage / 100) * circumference;
    
    circle.style.strokeDashoffset = offset;
}

function updateSessionTypeDisplay() {
    const typeDisplay = document.getElementById('pomodoroSessionType');
    if (!typeDisplay) return;
    
    if (currentSessionType === 'work') {
        typeDisplay.textContent = '🎯 Focus Session';
        typeDisplay.style.color = 'var(--accent-primary)';
    } else {
        typeDisplay.textContent = '☕ Break Time';
        typeDisplay.style.color = 'var(--accent-secondary)';
    }
}

function updatePomodoroButtons() {
    const startBtn = document.getElementById('pomodoroStartBtn');
    const pauseBtn = document.getElementById('pomodoroPauseBtn');
    const resetBtn = document.getElementById('pomodoroResetBtn');
    
    if (pomodoroRunning) {
        if (startBtn) startBtn.style.display = 'none';
        if (pauseBtn) pauseBtn.style.display = 'inline-flex';
    } else {
        if (startBtn) startBtn.style.display = 'inline-flex';
        if (pauseBtn) pauseBtn.style.display = 'none';
    }
    
    if (resetBtn) {
        resetBtn.disabled = pomodoroSeconds === 0 && !pomodoroRunning;
    }
}

function playCompletionSound() {
    // Simple beep sound (optional - can be enhanced)
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (error) {
        console.log('Audio not available');
    }
}

// Initialize display on load
updateTimerDisplay();
updateSessionTypeDisplay();
updatePomodoroButtons();

// Expose functions globally
window.setupPomodoroEventListeners = setupPomodoroEventListeners;
window.startPomodoro = startPomodoro;
window.pausePomodoro = pausePomodoro;
window.resetPomodoro = resetPomodoro;
window.skipToBreak = skipToBreak;
