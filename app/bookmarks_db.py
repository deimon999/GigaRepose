import sqlite3
from datetime import datetime

DB_PATH = 'jarvis_bookmarks.db'

def init_db():
    """Initialize bookmarks database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'General',
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add indexes for better query performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_bookmarks_category 
        ON bookmarks(category)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_bookmarks_updated_at 
        ON bookmarks(updated_at DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_bookmarks_title 
        ON bookmarks(title)
    ''')
    
    conn.commit()
    conn.close()
    print(f"✓ Bookmarks database initialized: {DB_PATH}")

def add_bookmark(title, url, description='', category='General', tags=''):
    """Add a new bookmark"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO bookmarks (title, url, description, category, tags)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, url, description, category, tags))
    
    bookmark_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return bookmark_id

def get_all_bookmarks():
    """Get all bookmarks"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, url, description, category, tags, created_at, updated_at
        FROM bookmarks
        ORDER BY created_at DESC
    ''')
    
    bookmarks = []
    for row in cursor.fetchall():
        bookmarks.append({
            'id': row[0],
            'title': row[1],
            'url': row[2],
            'description': row[3],
            'category': row[4],
            'tags': row[5],
            'created_at': row[6],
            'updated_at': row[7]
        })
    
    conn.close()
    return bookmarks

def get_bookmark(bookmark_id):
    """Get a specific bookmark by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, url, description, category, tags, created_at, updated_at
        FROM bookmarks
        WHERE id = ?
    ''', (bookmark_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'title': row[1],
            'url': row[2],
            'description': row[3],
            'category': row[4],
            'tags': row[5],
            'created_at': row[6],
            'updated_at': row[7]
        }
    return None

def update_bookmark(bookmark_id, title, url, description, category, tags):
    """Update an existing bookmark"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE bookmarks
        SET title = ?, url = ?, description = ?, category = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (title, url, description, category, tags, bookmark_id))
    
    conn.commit()
    conn.close()

def delete_bookmark(bookmark_id):
    """Delete a bookmark"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM bookmarks WHERE id = ?', (bookmark_id,))
    
    conn.commit()
    conn.close()

def search_bookmarks(query):
    """Search bookmarks by title, url, description, or tags"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    search_query = f'%{query}%'
    cursor.execute('''
        SELECT id, title, url, description, category, tags, created_at, updated_at
        FROM bookmarks
        WHERE title LIKE ? OR url LIKE ? OR description LIKE ? OR tags LIKE ?
        ORDER BY created_at DESC
    ''', (search_query, search_query, search_query, search_query))
    
    bookmarks = []
    for row in cursor.fetchall():
        bookmarks.append({
            'id': row[0],
            'title': row[1],
            'url': row[2],
            'description': row[3],
            'category': row[4],
            'tags': row[5],
            'created_at': row[6],
            'updated_at': row[7]
        })
    
    conn.close()
    return bookmarks
