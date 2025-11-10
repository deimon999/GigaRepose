import sqlite3
import json
from datetime import datetime
from pathlib import Path

class NotesDatabase:
    def __init__(self, db_path="jarvis_notes.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with notes table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'General',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Notes database initialized: {self.db_path}")
    
    def create_note(self, title, content, category="General"):
        """Create a new note"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notes (title, content, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, category, datetime.now(), datetime.now()))
        
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return note_id
    
    def get_all_notes(self):
        """Get all notes"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, category, created_at, updated_at
            FROM notes
            ORDER BY updated_at DESC
        ''')
        
        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return notes
    
    def get_note_by_id(self, note_id):
        """Get a specific note by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, content, category, created_at, updated_at
            FROM notes
            WHERE id = ?
        ''', (note_id,))
        
        note = cursor.fetchone()
        conn.close()
        
        return dict(note) if note else None
    
    def update_note(self, note_id, title=None, content=None, category=None):
        """Update an existing note"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic update query
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now())
            params.append(note_id)
            
            query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
        
        conn.close()
        
        return cursor.rowcount > 0
    
    def delete_note(self, note_id):
        """Delete a note"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def search_notes(self, query):
        """Search notes by title or content"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        cursor.execute('''
            SELECT id, title, content, category, created_at, updated_at
            FROM notes
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY updated_at DESC
        ''', (search_pattern, search_pattern))
        
        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return notes
