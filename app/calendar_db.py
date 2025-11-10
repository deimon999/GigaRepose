import sqlite3
from datetime import datetime
from pathlib import Path

class CalendarDatabase:
    def __init__(self, db_path="jarvis_calendar.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with events table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                event_date DATE NOT NULL,
                event_time TIME,
                duration INTEGER DEFAULT 60,
                category TEXT DEFAULT 'Study',
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Calendar database initialized: {self.db_path}")
    
    def create_event(self, title, event_date, event_time=None, description="", duration=60, category="Study"):
        """Create a new event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (title, description, event_date, event_time, duration, category, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, event_date, event_time, duration, category, datetime.now()))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return event_id
    
    def get_all_events(self):
        """Get all events ordered by date"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, event_date, event_time, duration, category, completed, created_at
            FROM events
            ORDER BY event_date ASC, event_time ASC
        ''')
        
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return events
    
    def get_events_by_date(self, date):
        """Get events for a specific date"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, event_date, event_time, duration, category, completed, created_at
            FROM events
            WHERE event_date = ?
            ORDER BY event_time ASC
        ''', (date,))
        
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return events
    
    def get_upcoming_events(self, limit=10):
        """Get upcoming events"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        cursor.execute('''
            SELECT id, title, description, event_date, event_time, duration, category, completed, created_at
            FROM events
            WHERE event_date >= ?
            ORDER BY event_date ASC, event_time ASC
            LIMIT ?
        ''', (today, limit))
        
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return events
    
    def get_event_by_id(self, event_id):
        """Get a specific event by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, event_date, event_time, duration, category, completed, created_at
            FROM events
            WHERE id = ?
        ''', (event_id,))
        
        event = cursor.fetchone()
        conn.close()
        
        return dict(event) if event else None
    
    def update_event(self, event_id, title=None, description=None, event_date=None, event_time=None, duration=None, category=None):
        """Update an existing event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic update query
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if event_date is not None:
            updates.append("event_date = ?")
            params.append(event_date)
        
        if event_time is not None:
            updates.append("event_time = ?")
            params.append(event_time)
        
        if duration is not None:
            updates.append("duration = ?")
            params.append(duration)
        
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        
        if updates:
            params.append(event_id)
            query = f"UPDATE events SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return cursor.rowcount > 0
    
    def toggle_completed(self, event_id):
        """Toggle event completed status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE events SET completed = NOT completed WHERE id = ?', (event_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_event(self, event_id):
        """Delete an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
