import sqlite3
from datetime import datetime
from pathlib import Path

class TodoDatabase:
    def __init__(self, db_path="jarvis_todos.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database with todos table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                priority TEXT DEFAULT 'Medium',
                due_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add indexes for better query performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_todos_completed 
            ON todos(completed)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_todos_priority 
            ON todos(priority)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_todos_due_date 
            ON todos(due_date)
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Todo database initialized: {self.db_path}")
    
    def create_todo(self, task, priority="Medium", due_date=None):
        """Create a new todo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO todos (task, priority, due_date, created_at)
            VALUES (?, ?, ?, ?)
        ''', (task, priority, due_date, datetime.now()))
        
        todo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return todo_id
    
    def get_all_todos(self):
        """Get all todos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, task, completed, priority, due_date, created_at
            FROM todos
            ORDER BY completed ASC, created_at DESC
        ''')
        
        todos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return todos
    
    def get_todo_by_id(self, todo_id):
        """Get a specific todo by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, task, completed, priority, due_date, created_at
            FROM todos
            WHERE id = ?
        ''', (todo_id,))
        
        todo = cursor.fetchone()
        conn.close()
        
        return dict(todo) if todo else None
    
    def update_todo(self, todo_id, task=None, priority=None, due_date=None):
        """Update an existing todo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic update query
        updates = []
        params = []
        
        if task is not None:
            updates.append("task = ?")
            params.append(task)
        
        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)
        
        if due_date is not None:
            updates.append("due_date = ?")
            params.append(due_date)
        
        if updates:
            params.append(todo_id)
            query = f"UPDATE todos SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return cursor.rowcount > 0
    
    def toggle_completed(self, todo_id):
        """Toggle todo completed status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE todos SET completed = NOT completed WHERE id = ?', (todo_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_todo(self, todo_id):
        """Delete a todo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def delete_completed(self):
        """Delete all completed todos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM todos WHERE completed = 1')
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
