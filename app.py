import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from pathlib import Path
import time
from functools import wraps

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache static files for 1 year

# Ensure upload folder exists
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# Performance monitoring decorator
def monitor_performance(route_name):
    """Decorator to monitor route performance"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # Convert to ms
            if duration > 1000:  # Log slow requests (>1s)
                print(f"⚠️  SLOW REQUEST: {route_name} took {duration:.2f}ms")
            elif duration > 100:  # Log moderate requests (>100ms)
                print(f"ℹ️  {route_name} took {duration:.2f}ms")
            return result
        return wrapped
    return decorator

# Import components (with graceful fallback for development)
try:
    from models.llm_client import LLMClient
    llm_client = LLMClient()
    print("âœ“ LLM client initialized successfully")
except Exception as e:
    print(f"âš  Warning: Could not initialize LLM client: {e}")

# Initialize Bookmarks Database
try:
    from app import bookmarks_db
    bookmarks_db.init_db()
except Exception as e:
    print(f"âš  Warning: Could not initialize Bookmarks database: {e}")

# Initialize Pomodoro Database
try:
    from app import pomodoro_db
    pomodoro_db.init_db()
except Exception as e:
    print(f"âš  Warning: Could not initialize Pomodoro database: {e}")

# Initialize Chat History Database
try:
    from app.chat_db import ChatDatabase
    chat_db = ChatDatabase()
except Exception as e:
    print(f"⚠ Warning: Could not initialize Chat history database: {e}")
    chat_db = None

# Initialize Notes Database
try:
    from app.notes_db import NotesDatabase
    notes_db = NotesDatabase()
    print("✓ Notes database initialized: jarvis_notes.db")
except Exception as e:
    print(f"⚠ Warning: Could not initialize Notes database: {e}")
    notes_db = None

# Initialize Todo Database
try:
    from app.todo_db import TodoDatabase
    todo_db = TodoDatabase()
except Exception as e:
    print(f"âš  Warning: Could not initialize Todo database: {e}")
    todo_db = None

# Retriever is optional - will work without it
# Temporarily disabled due to sentence-transformers compatibility issues
retriever = None
if os.getenv("ENABLE_RETRIEVER") == "1":
    try:
        from models.retriever import Retriever
        retriever = Retriever()
        print("âœ“ Retriever initialized successfully")
    except Exception as e:
        print(f"âš  Warning: Could not initialize retriever (will work without document search): {e}")
        retriever = None
else:
    print("â„¹ Document search disabled (set ENABLE_RETRIEVER=1 to enable)")

# Initialize document manager
try:
    from models.document_manager import DocumentManager
    doc_manager = DocumentManager()
    print("âœ“ Document manager initialized successfully")
except Exception as e:
    print(f"âš  Warning: Could not initialize document manager: {e}")
    doc_manager = None

@app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'ollama_connected': llm_client is not None,
        'pinecone_connected': retriever is not None
    })

@app.route('/chat', methods=['POST'])
@monitor_performance('POST /chat')
def chat():
    """Handle chat requests"""
    try:
        data = request.json
        user_message = data.get('message', '')
        history = data.get('history', [])
        chat_id = data.get('chat_id')  # Optional: ID of current chat
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Create a new chat if chat_id not provided
        if chat_db and not chat_id:
            # Generate a title from the first message (first 50 chars)
            title = user_message[:50] + ('...' if len(user_message) > 50 else '')
            chat_id = chat_db.create_chat(title)
        
        # Save user message to database
        if chat_db and chat_id:
            chat_db.add_message(chat_id, 'user', user_message)
        
        # Get relevant context from Pinecone (if available)
        context = ""
        if retriever:
            try:
                relevant_docs = retriever.get_relevant_documents(user_message)
                if relevant_docs:
                    context = "\n\nRelevant information from your documents:\n" + "\n".join(relevant_docs)
            except Exception as e:
                print(f"Warning: Could not retrieve context: {e}")
        
        # Prepare system prompt with context
        system_prompt = """You are Jarvis, a study notes assistant. 

IMPORTANT FORMATTING RULES:
- Start with a clear heading
- Each bullet point must be on a NEW LINE
- Use simple bullet points (â€¢) or numbers (1., 2., 3.)
- One concept per line
- Keep each point SHORT (max 10-15 words)
- Add blank lines between major sections
- NO long paragraphs
- NO multiple points on same line

Example response format:
ðŸ“š Number System Topics:

1ï¸âƒ£ Natural Numbers
â€¢ Counting numbers: 1, 2, 3...

2ï¸âƒ£ Prime Numbers
â€¢ Divisible only by 1 and itself
â€¢ Examples: 2, 3, 5, 7, 11

3ï¸âƒ£ Even & Odd
â€¢ Even: ends in 0, 2, 4, 6, 8
â€¢ Odd: ends in 1, 3, 5, 7, 9

Keep it simple, clean, and well-spaced."""
        if context:
            system_prompt += "\n\n" + context
        
        # Get response from LLM
        if llm_client:
            response = llm_client.get_completion_sync(
                user_message,
                history=history,
                system_prompt=system_prompt
            )
            
            # Post-process response to ensure proper line breaks
            # Add line breaks after bullet points and numbers
            response = response.replace('â€¢ ', '\nâ€¢ ')
            response = response.replace('1ï¸âƒ£', '\n\n1ï¸âƒ£')
            response = response.replace('2ï¸âƒ£', '\n\n2ï¸âƒ£')
            response = response.replace('3ï¸âƒ£', '\n\n3ï¸âƒ£')
            response = response.replace('4ï¸âƒ£', '\n\n4ï¸âƒ£')
            response = response.replace('5ï¸âƒ£', '\n\n5ï¸âƒ£')
            response = response.replace('6ï¸âƒ£', '\n\n6ï¸âƒ£')
            response = response.replace('7ï¸âƒ£', '\n\n7ï¸âƒ£')
            response = response.replace('8ï¸âƒ£', '\n\n8ï¸âƒ£')
            response = response.replace('9ï¸âƒ£', '\n\n9ï¸âƒ£')
            response = response.strip()  # Remove leading/trailing whitespace
            
            # Save assistant response to database
            if chat_db and chat_id:
                chat_db.add_message(chat_id, 'assistant', response)
            
            return jsonify({
                'response': response,
                'chat_id': chat_id,
                'status': 'success'
            })
        else:
            return jsonify({
                'response': "I'm not fully initialized yet. Please check that Ollama is running.",
                'status': 'warning'
            })
            
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    """Generate a summary of provided text"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not llm_client:
            return jsonify({'error': 'LLM not available'}), 503
        
        # Create summary prompt
        prompt = f"""Please provide a concise summary of the following text. 
Focus on the key points and main ideas:

{text}

Summary:"""
        
        summary = llm_client.get_completion_sync(prompt)
        
        return jsonify({
            'summary': summary,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in summarize endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate-flashcards', methods=['POST'])
def generate_flashcards():
    """Generate flashcards from provided text"""
    try:
        data = request.json
        text = data.get('text', '')
        num_cards = data.get('num_cards', 5)
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not llm_client:
            return jsonify({'error': 'LLM not available'}), 503
        
        # Create flashcard generation prompt
        prompt = f"""Generate {num_cards} flashcards from the following text. 
Each flashcard should have a clear question and a concise answer.
Format as JSON array with "question" and "answer" fields.

Text:
{text}

Generate flashcards in this exact JSON format:
[
  {{"question": "Question 1?", "answer": "Answer 1"}},
  {{"question": "Question 2?", "answer": "Answer 2"}}
]"""
        
        response = llm_client.get_completion_sync(prompt)
        
        # Try to parse JSON response
        import json
        try:
            # Extract JSON from response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end > start:
                flashcards_json = response[start:end]
                flashcards = json.loads(flashcards_json)
            else:
                # Fallback: create simple flashcards
                flashcards = [{"question": "Summary", "answer": response}]
        except:
            flashcards = [{"question": "Generated Content", "answer": response}]
        
        return jsonify({
            'flashcards': flashcards,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in generate-flashcards endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/explain', methods=['POST'])
def explain_topic():
    """Generate detailed explanation with enhanced context retrieval"""
    try:
        data = request.json
        topic = data.get('topic', '')
        
        if not topic:
            return jsonify({'error': 'No topic provided'}), 400
        
        if not llm_client:
            return jsonify({'error': 'LLM not available'}), 503
        
        # Enhanced context retrieval from Pinecone
        context_docs = []
        if retriever:
            try:
                # Retrieve MORE context for detailed explanation (top_k=5 instead of 3)
                context_docs = retriever.retrieve(topic, top_k=5)
            except Exception as e:
                print(f"Error retrieving context: {e}")
        
        # Build context string
        context = "\n\n".join([doc['text'] for doc in context_docs]) if context_docs else ""
        
        # Create detailed explanation prompt
        if context:
            prompt = f"""Based on the following reference materials, provide a comprehensive and detailed explanation of: {topic}

Reference Materials:
{context}

Instructions:
- Explain the topic thoroughly with examples
- Break down complex concepts into understandable parts
- Include key definitions and important points
- Use clear, educational language
- Structure the explanation logically

Detailed Explanation:"""
        else:
            prompt = f"""Provide a comprehensive and detailed explanation of: {topic}

Instructions:
- Explain the topic thoroughly with examples
- Break down complex concepts into understandable parts
- Include key definitions and important points
- Use clear, educational language
- Structure the explanation logically

Detailed Explanation:"""
        
        explanation = llm_client.get_completion_sync(prompt)
        
        return jsonify({
            'explanation': explanation,
            'context_found': len(context_docs) > 0,
            'sources': len(context_docs),
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Error in explain endpoint: {e}")
        return jsonify({'error': str(e)}), 500

# ============= CHAT HISTORY API ENDPOINTS =============

@app.route('/chat-history', methods=['GET'])
def get_chat_history():
    """Get all chat conversations"""
    try:
        if not chat_db:
            return jsonify({'error': 'Chat history not available'}), 503
        
        chats = chat_db.get_all_chats()
        return jsonify({'chats': chats, 'status': 'success'})
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat-history/<int:chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Get a specific chat with all messages"""
    try:
        if not chat_db:
            return jsonify({'error': 'Chat history not available'}), 503
        
        chat = chat_db.get_chat(chat_id)
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        messages = chat_db.get_chat_messages(chat_id)
        
        return jsonify({
            'chat': chat,
            'messages': messages,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error getting chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat-history', methods=['POST'])
def create_chat():
    """Create a new chat conversation"""
    try:
        if not chat_db:
            return jsonify({'error': 'Chat history not available'}), 503
        
        data = request.json
        title = data.get('title', 'New Conversation')
        
        chat_id = chat_db.create_chat(title)
        
        return jsonify({
            'chat_id': chat_id,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error creating chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat-history/<int:chat_id>', methods=['PUT'])
def update_chat(chat_id):
    """Update a chat's title"""
    try:
        if not chat_db:
            return jsonify({'error': 'Chat history not available'}), 503
        
        data = request.json
        title = data.get('title', '')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        chat_db.update_chat_title(chat_id, title)
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error updating chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat-history/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a chat conversation"""
    try:
        if not chat_db:
            return jsonify({'error': 'Chat history not available'}), 503
        
        if chat_db.delete_chat(chat_id):
            return jsonify({'status': 'success'})
        return jsonify({'error': 'Chat not found'}), 404
    except Exception as e:
        print(f"Error deleting chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat-history/clear', methods=['POST'])
def clear_chat_history():
    """Clear all chat history"""
    try:
        if not chat_db:
            return jsonify({'error': 'Chat history not available'}), 503
        
        chat_db.clear_all_history()
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat-history/search', methods=['POST'])
def search_chat_history():
    """Search through chat messages"""
    try:
        if not chat_db:
            return jsonify({'error': 'Chat history not available'}), 503
        
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        results = chat_db.search_messages(query)
        
        return jsonify({
            'results': results,
            'count': len(results),
            'status': 'success'
        })
    except Exception as e:
        print(f"Error searching chat history: {e}")
        return jsonify({'error': str(e)}), 500

# ============= DOCUMENTS API ENDPOINTS =============

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/documents', methods=['GET'])
def get_documents():
    """Get list of all uploaded documents"""
    if doc_manager:
        documents = doc_manager.get_all_documents()
        return jsonify({'documents': documents, 'count': len(documents)})
    return jsonify({'documents': [], 'count': 0})

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a new document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF and TXT files allowed.'}), 400
        
        # Generate unique filename if file already exists
        filename = secure_filename(file.filename)
        base_name, extension = os.path.splitext(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Add timestamp suffix if file exists to avoid conflicts
        counter = 1
        while os.path.exists(filepath):
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"{base_name}_{timestamp}{extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            filename = new_filename
            counter += 1
            if counter > 100:  # Safety limit
                return jsonify({'error': 'Too many files with similar names'}), 400
        
        # Save file with unique name
        try:
            file.save(filepath)
        except PermissionError:
            return jsonify({'error': f'Permission denied: File "{filename}" may be open in another program. Please close it and try again.'}), 403
        except Exception as save_error:
            return jsonify({'error': f'Failed to save file: {str(save_error)}'}), 500
        
        # Add to document manager
        if doc_manager:
            file_size = os.path.getsize(filepath)
            doc_info = doc_manager.add_document(filepath, filename, file_size)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'document': doc_info
            })
        
        return jsonify({'message': 'File uploaded but metadata not saved'}), 201
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document"""
    try:
        if doc_manager and doc_manager.delete_document(doc_id):
            return jsonify({'message': 'Document deleted successfully'})
        return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        print(f"Error deleting document: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/ingest-all', methods=['POST'])
def ingest_all_documents():
    """Re-ingest all documents into Pinecone"""
    try:
        from models.ingest import DocumentIngestor
        
        print("Starting document ingestion...")
        ingestor = DocumentIngestor()
        ingestor.ingest_documents(data_dir='data')
        
        return jsonify({
            'message': 'All documents have been re-ingested successfully!',
            'status': 'success'
        })
    except ValueError as ve:
        # Handle missing API key
        error_msg = str(ve)
        print(f"ValueError during ingestion: {error_msg}")
        if "PINECONE_API_KEY" in error_msg:
            return jsonify({
                'error': 'Pinecone API key not configured. Add PINECONE_API_KEY to your .env file.',
                'status': 'error'
            }), 503
        return jsonify({'error': error_msg, 'status': 'error'}), 400
    except ImportError as ie:
        # Handle missing dependencies
        print(f"ImportError during ingestion: {ie}")
        return jsonify({
            'error': f'Required libraries not installed: {str(ie)}',
            'status': 'error'
        }), 503
    except Exception as e:
        print(f"Error ingesting documents: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'status': 'error'}), 500

# ============= NOTES API ENDPOINTS =============

@app.route('/notes', methods=['GET'])
@monitor_performance('GET /notes')
def get_notes():
    """Get all notes"""
    try:
        if not notes_db:
            return jsonify({'error': 'Notes database not available'}), 503
        
        notes = notes_db.get_all_notes()
        return jsonify({'notes': notes, 'status': 'success'})
    except Exception as e:
        print(f"Error getting notes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    try:
        if not notes_db:
            return jsonify({'error': 'Notes database not available'}), 503
        
        data = request.json
        title = data.get('title', 'Untitled')
        content = data.get('content', '')
        category = data.get('category', 'General')
        
        if not content:
            return jsonify({'error': 'Note content cannot be empty'}), 400
        
        note_id = notes_db.create_note(title, content, category)
        
        return jsonify({
            'message': 'Note created successfully',
            'note_id': note_id,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error creating note: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note"""
    try:
        if not notes_db:
            return jsonify({'error': 'Notes database not available'}), 503
        
        note = notes_db.get_note_by_id(note_id)
        if note:
            return jsonify({'note': note, 'status': 'success'})
        return jsonify({'error': 'Note not found'}), 404
    except Exception as e:
        print(f"Error getting note: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a note"""
    try:
        if not notes_db:
            return jsonify({'error': 'Notes database not available'}), 503
        
        data = request.json
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        
        notes_db.update_note(note_id, title, content, category)
        
        return jsonify({
            'message': 'Note updated successfully',
            'status': 'success'
        })
    except Exception as e:
        print(f"Error updating note: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note"""
    try:
        if not notes_db:
            return jsonify({'error': 'Notes database not available'}), 503
        
        notes_db.delete_note(note_id)
        
        return jsonify({
            'message': 'Note deleted successfully',
            'status': 'success'
        })
    except Exception as e:
        print(f"Error deleting note: {e}")
        return jsonify({'error': str(e)}), 500

"""
@app.route('/notes/search', methods=['GET'])
def search_notes():
    # DEPRECATED: Use /bookmarks/search instead
    pass
"""

# ============= TODO API ENDPOINTS =============

@app.route('/todos', methods=['GET'])
@monitor_performance('GET /todos')
def get_todos():
    """Get all todos"""
    try:
        if not todo_db:
            return jsonify({'error': 'Todo database not available'}), 503
        
        todos = todo_db.get_all_todos()
        return jsonify({'todos': todos, 'status': 'success'})
    except Exception as e:
        print(f"Error getting todos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    try:
        if not todo_db:
            return jsonify({'error': 'Todo database not available'}), 503
        
        data = request.json
        task = data.get('task', '')
        priority = data.get('priority', 'Medium')
        due_date = data.get('due_date')
        
        if not task:
            return jsonify({'error': 'Task cannot be empty'}), 400
        
        todo_id = todo_db.create_todo(task, priority, due_date)
        
        return jsonify({
            'message': 'Todo created successfully',
            'todo_id': todo_id,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error creating todo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a specific todo by ID"""
    try:
        if not todo_db:
            return jsonify({'error': 'Todo database not available'}), 503
        
        todo = todo_db.get_todo_by_id(todo_id)
        
        if todo:
            return jsonify({'todo': todo, 'status': 'success'})
        else:
            return jsonify({'error': 'Todo not found'}), 404
    except Exception as e:
        print(f"Error getting todo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update an existing todo"""
    try:
        if not todo_db:
            return jsonify({'error': 'Todo database not available'}), 503
        
        data = request.json
        task = data.get('task')
        priority = data.get('priority')
        due_date = data.get('due_date')
        
        success = todo_db.update_todo(todo_id, task, priority, due_date)
        
        if success:
            return jsonify({
                'message': 'Todo updated successfully',
                'status': 'success'
            })
        else:
            return jsonify({'error': 'Todo not found'}), 404
    except Exception as e:
        print(f"Error updating todo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>/toggle', methods=['POST'])
def toggle_todo(todo_id):
    """Toggle todo completed status"""
    try:
        if not todo_db:
            return jsonify({'error': 'Todo database not available'}), 503
        
        success = todo_db.toggle_completed(todo_id)
        
        if success:
            return jsonify({
                'message': 'Todo status toggled',
                'status': 'success'
            })
        else:
            return jsonify({'error': 'Todo not found'}), 404
    except Exception as e:
        print(f"Error toggling todo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo"""
    try:
        if not todo_db:
            return jsonify({'error': 'Todo database not available'}), 503
        
        success = todo_db.delete_todo(todo_id)
        
        if success:
            return jsonify({
                'message': 'Todo deleted successfully',
                'status': 'success'
            })
        else:
            return jsonify({'error': 'Todo not found'}), 404
    except Exception as e:
        print(f"Error deleting todo: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/todos/completed', methods=['DELETE'])
def delete_completed_todos():
    """Delete all completed todos"""
    try:
        if not todo_db:
            return jsonify({'error': 'Todo database not available'}), 503
        
        count = todo_db.delete_completed()
        
        return jsonify({
            'message': f'Deleted {count} completed todo(s)',
            'count': count,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error deleting completed todos: {e}")
        return jsonify({'error': str(e)}), 500


# ============== POMODORO ROUTES ==============
@app.route('/pomodoro/start', methods=['POST'])
def start_pomodoro():
    """Start a new pomodoro session"""
    try:
        from app import pomodoro_db
        data = request.get_json()
        task_name = data.get('task_name', 'Focus Session')
        duration = data.get('duration', 25)
        session_type = data.get('session_type', 'work')
        
        session_id = pomodoro_db.start_session(task_name, duration, session_type)
        
        return jsonify({
            'status': 'success',
            'message': 'Pomodoro session started',
            'session_id': session_id
        })
    except Exception as e:
        print(f"Error starting pomodoro: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/pomodoro/complete/<int:session_id>', methods=['POST'])
def complete_pomodoro(session_id):
    """Complete a pomodoro session"""
    try:
        from app import pomodoro_db
        pomodoro_db.complete_session(session_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Pomodoro session completed',
            'session_id': session_id
        })
    except Exception as e:
        print(f"Error completing pomodoro: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/pomodoro/stats', methods=['GET'])
def get_pomodoro_stats():
    """Get today's pomodoro statistics"""
    try:
        from app import pomodoro_db
        stats = pomodoro_db.get_today_stats()
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    except Exception as e:
        print(f"Error getting pomodoro stats: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/pomodoro/sessions', methods=['GET'])
def get_pomodoro_sessions():
    """Get recent pomodoro sessions"""
    try:
        from app import pomodoro_db
        limit = request.args.get('limit', 10, type=int)
        sessions = pomodoro_db.get_recent_sessions(limit)
        
        return jsonify({
            'status': 'success',
            'sessions': sessions
        })
    except Exception as e:
        print(f"Error getting pomodoro sessions: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/pomodoro/sessions/<int:session_id>', methods=['DELETE'])
def delete_pomodoro_session(session_id):
    """Delete a pomodoro session"""
    try:
        from app import pomodoro_db
        pomodoro_db.delete_session(session_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Session deleted'
        })
    except Exception as e:
        print(f"Error deleting pomodoro session: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500


# ============== BOOKMARKS ROUTES ==============
@app.route('/bookmarks', methods=['GET'])
@monitor_performance('GET /bookmarks')
def get_bookmarks():
    """Get all bookmarks"""
    try:
        from app import bookmarks_db
        bookmarks = bookmarks_db.get_all_bookmarks()
        
        return jsonify({
            'status': 'success',
            'bookmarks': bookmarks
        })
    except Exception as e:
        print(f"Error getting bookmarks: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/bookmarks', methods=['POST'])
def create_bookmark():
    """Create a new bookmark"""
    try:
        from app import bookmarks_db
        data = request.get_json()
        
        title = data.get('title')
        url = data.get('url')
        description = data.get('description', '')
        category = data.get('category', 'General')
        tags = data.get('tags', '')
        
        if not title or not url:
            return jsonify({'status': 'error', 'error': 'Title and URL are required'}), 400
        
        bookmark_id = bookmarks_db.add_bookmark(title, url, description, category, tags)
        
        return jsonify({
            'status': 'success',
            'message': 'Bookmark created',
            'bookmark_id': bookmark_id
        })
    except Exception as e:
        print(f"Error creating bookmark: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/bookmarks/<int:bookmark_id>', methods=['GET'])
def get_bookmark(bookmark_id):
    """Get a specific bookmark"""
    try:
        from app import bookmarks_db
        bookmark = bookmarks_db.get_bookmark(bookmark_id)
        
        if not bookmark:
            return jsonify({'status': 'error', 'error': 'Bookmark not found'}), 404
        
        return jsonify({
            'status': 'success',
            'bookmark': bookmark
        })
    except Exception as e:
        print(f"Error getting bookmark: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/bookmarks/<int:bookmark_id>', methods=['PUT'])
def update_bookmark(bookmark_id):
    """Update a bookmark"""
    try:
        from app import bookmarks_db
        data = request.get_json()
        
        title = data.get('title')
        url = data.get('url')
        description = data.get('description', '')
        category = data.get('category', 'General')
        tags = data.get('tags', '')
        
        if not title or not url:
            return jsonify({'status': 'error', 'error': 'Title and URL are required'}), 400
        
        bookmarks_db.update_bookmark(bookmark_id, title, url, description, category, tags)
        
        return jsonify({
            'status': 'success',
            'message': 'Bookmark updated'
        })
    except Exception as e:
        print(f"Error updating bookmark: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/bookmarks/<int:bookmark_id>', methods=['DELETE'])
def delete_bookmark(bookmark_id):
    """Delete a bookmark"""
    try:
        from app import bookmarks_db
        bookmarks_db.delete_bookmark(bookmark_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Bookmark deleted'
        })
    except Exception as e:
        print(f"Error deleting bookmark: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/bookmarks/search', methods=['GET'])
def search_bookmarks():
    """Search bookmarks"""
    try:
        from app import bookmarks_db
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'status': 'error', 'error': 'Search query is required'}), 400
        
        bookmarks = bookmarks_db.search_bookmarks(query)
        
        return jsonify({
            'status': 'success',
            'bookmarks': bookmarks
        })
    except Exception as e:
        print(f"Error searching bookmarks: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500


# ============= DEPRECATED: CALENDAR/EVENTS ROUTES - Replaced with Pomodoro =============
# Note: These routes have been commented out. Use /pomodoro/* endpoints instead.
"""
@app.route('/events', methods=['GET'])
def get_events():
    pass  # DEPRECATED
"""

if __name__ == '__main__':
    print("🔮 Starting Nexus...")
    print(f"🤖 Ollama URL: http://localhost:11434")
    print(f"🌐 Server running at: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
