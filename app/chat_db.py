"""
Chat History Database
Stores all chat conversations with timestamps
"""

import sqlite3
from datetime import datetime
import json

DB_NAME = 'jarvis_chat.db'

def init_db():
    """Initialize the chat history database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create chats table (conversations)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chats_updated_at ON chats(updated_at)')
    
    conn.commit()
    conn.close()
    print(f"✓ Chat history database initialized: {DB_NAME}")

class ChatDatabase:
    def __init__(self):
        """Initialize database connection"""
        init_db()
    
    def create_chat(self, title="New Conversation"):
        """Create a new chat conversation"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chats (title, created_at, updated_at)
            VALUES (?, ?, ?)
        ''', (title, datetime.now(), datetime.now()))
        
        chat_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return chat_id
    
    def add_message(self, chat_id, role, content):
        """Add a message to a chat"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Add message
        cursor.execute('''
            INSERT INTO messages (chat_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, role, content, datetime.now()))
        
        # Update chat's updated_at timestamp
        cursor.execute('''
            UPDATE chats SET updated_at = ? WHERE id = ?
        ''', (datetime.now(), chat_id))
        
        conn.commit()
        conn.close()
    
    def get_all_chats(self):
        """Get all chat conversations"""
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.id,
                c.title,
                c.created_at,
                c.updated_at,
                COUNT(m.id) as message_count,
                (SELECT content FROM messages WHERE chat_id = c.id ORDER BY timestamp ASC LIMIT 1) as first_message
            FROM chats c
            LEFT JOIN messages m ON c.id = m.chat_id
            GROUP BY c.id
            ORDER BY c.updated_at DESC
        ''')
        
        chats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return chats
    
    def get_chat_messages(self, chat_id):
        """Get all messages from a specific chat"""
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, role, content, timestamp
            FROM messages
            WHERE chat_id = ?
            ORDER BY timestamp ASC
        ''', (chat_id,))
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return messages
    
    def get_chat(self, chat_id):
        """Get a specific chat by ID"""
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM chats WHERE id = ?', (chat_id,))
        chat = cursor.fetchone()
        conn.close()
        
        return dict(chat) if chat else None
    
    def update_chat_title(self, chat_id, title):
        """Update a chat's title"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chats SET title = ?, updated_at = ? WHERE id = ?
        ''', (title, datetime.now(), chat_id))
        
        conn.commit()
        conn.close()
    
    def delete_chat(self, chat_id):
        """Delete a chat and all its messages"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Messages will be deleted automatically due to CASCADE
        cursor.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def clear_all_history(self):
        """Clear all chat history"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM messages')
        cursor.execute('DELETE FROM chats')
        
        conn.commit()
        conn.close()
    
    def search_messages(self, query):
        """Search messages by content"""
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                m.id,
                m.chat_id,
                m.role,
                m.content,
                m.timestamp,
                c.title as chat_title
            FROM messages m
            JOIN chats c ON m.chat_id = c.id
            WHERE m.content LIKE ?
            ORDER BY m.timestamp DESC
            LIMIT 50
        ''', (f'%{query}%',))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
