import sqlite3
from datetime import datetime

DB_PATH = 'jarvis_pomodoro.db'

def init_db():
    """Initialize pomodoro database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pomodoro_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            duration INTEGER DEFAULT 25,
            session_type TEXT DEFAULT 'work',
            completed BOOLEAN DEFAULT 0,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pomodoro_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            total_sessions INTEGER DEFAULT 0,
            total_minutes INTEGER DEFAULT 0,
            UNIQUE(date)
        )
    ''')
    
    # Add indexes for better query performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_pomodoro_sessions_date 
        ON pomodoro_sessions(DATE(created_at))
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_pomodoro_sessions_completed 
        ON pomodoro_sessions(completed)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_pomodoro_stats_date 
        ON pomodoro_stats(date)
    ''')
    
    conn.commit()
    conn.close()
    print(f"✓ Pomodoro database initialized: {DB_PATH}")

def start_session(task_name, duration=25, session_type='work'):
    """Start a new pomodoro session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO pomodoro_sessions (task_name, duration, session_type, started_at)
        VALUES (?, ?, ?, ?)
    ''', (task_name, duration, session_type, datetime.now()))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return session_id

def complete_session(session_id):
    """Mark a session as completed"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE pomodoro_sessions
        SET completed = 1, completed_at = ?
        WHERE id = ?
    ''', (datetime.now(), session_id))
    
    # Update daily stats
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT duration FROM pomodoro_sessions WHERE id = ?
    ''', (session_id,))
    duration = cursor.fetchone()[0]
    
    cursor.execute('''
        INSERT INTO pomodoro_stats (date, total_sessions, total_minutes)
        VALUES (?, 1, ?)
        ON CONFLICT(date) DO UPDATE SET
            total_sessions = total_sessions + 1,
            total_minutes = total_minutes + ?
    ''', (today, duration, duration))
    
    conn.commit()
    conn.close()

def get_today_stats():
    """Get today's pomodoro statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT total_sessions, total_minutes FROM pomodoro_stats WHERE date = ?
    ''', (today,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {'sessions': row[0], 'minutes': row[1]}
    return {'sessions': 0, 'minutes': 0}

def get_recent_sessions(limit=10):
    """Get recent pomodoro sessions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, task_name, duration, session_type, completed, started_at, completed_at
        FROM pomodoro_sessions
        ORDER BY started_at DESC
        LIMIT ?
    ''', (limit,))
    
    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            'id': row[0],
            'task_name': row[1],
            'duration': row[2],
            'session_type': row[3],
            'completed': bool(row[4]),
            'started_at': row[5],
            'completed_at': row[6]
        })
    
    conn.close()
    return sessions

def delete_session(session_id):
    """Delete a pomodoro session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM pomodoro_sessions WHERE id = ?', (session_id,))
    
    conn.commit()
    conn.close()
