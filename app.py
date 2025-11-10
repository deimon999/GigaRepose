import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from pathlib import Path

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

# Ensure upload folder exists
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# Import components (with graceful fallback for development)
try:
    from app.llm_client import LLMClient
    llm_client = LLMClient()
    print("✓ LLM client initialized successfully")
except Exception as e:
    print(f"⚠ Warning: Could not initialize LLM client: {e}")

# Initialize Notes Database
try:
    from app.notes_db import NotesDatabase
    notes_db = NotesDatabase()
except Exception as e:
    print(f"⚠ Warning: Could not initialize Notes database: {e}")
    notes_db = None

# Initialize Calendar Database
try:
    from app.calendar_db import CalendarDatabase
    calendar_db = CalendarDatabase()
except Exception as e:
    print(f"⚠ Warning: Could not initialize Calendar database: {e}")
    calendar_db = None

# Initialize Todo Database
try:
    from app.todo_db import TodoDatabase
    todo_db = TodoDatabase()
except Exception as e:
    print(f"⚠ Warning: Could not initialize Todo database: {e}")
    todo_db = None

# Retriever is optional - will work without it
# Temporarily disabled due to sentence-transformers compatibility issues
retriever = None
if os.getenv("ENABLE_RETRIEVER") == "1":
    try:
        from app.retriever import Retriever
        retriever = Retriever()
        print("✓ Retriever initialized successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not initialize retriever (will work without document search): {e}")
        retriever = None
else:
    print("ℹ Document search disabled (set ENABLE_RETRIEVER=1 to enable)")

# Initialize document manager
try:
    from app.document_manager import DocumentManager
    doc_manager = DocumentManager()
    print("✓ Document manager initialized successfully")
except Exception as e:
    print(f"⚠ Warning: Could not initialize document manager: {e}")
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
def chat():
    """Handle chat requests"""
    try:
        data = request.json
        user_message = data.get('message', '')
        history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
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
- Use simple bullet points (•) or numbers (1., 2., 3.)
- One concept per line
- Keep each point SHORT (max 10-15 words)
- Add blank lines between major sections
- NO long paragraphs
- NO multiple points on same line

Example response format:
📚 Number System Topics:

1️⃣ Natural Numbers
• Counting numbers: 1, 2, 3...

2️⃣ Prime Numbers
• Divisible only by 1 and itself
• Examples: 2, 3, 5, 7, 11

3️⃣ Even & Odd
• Even: ends in 0, 2, 4, 6, 8
• Odd: ends in 1, 3, 5, 7, 9

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
            response = response.replace('• ', '\n• ')
            response = response.replace('1️⃣', '\n\n1️⃣')
            response = response.replace('2️⃣', '\n\n2️⃣')
            response = response.replace('3️⃣', '\n\n3️⃣')
            response = response.replace('4️⃣', '\n\n4️⃣')
            response = response.replace('5️⃣', '\n\n5️⃣')
            response = response.replace('6️⃣', '\n\n6️⃣')
            response = response.replace('7️⃣', '\n\n7️⃣')
            response = response.replace('8️⃣', '\n\n8️⃣')
            response = response.replace('9️⃣', '\n\n9️⃣')
            response = response.strip()  # Remove leading/trailing whitespace
            
            return jsonify({
                'response': response,
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
        from app.ingest import DocumentIngestor
        
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
        title = data.get('title', 'Untitled Note')
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
    """Get a specific note by ID"""
    try:
        if not notes_db:
            return jsonify({'error': 'Notes database not available'}), 503
        
        note = notes_db.get_note_by_id(note_id)
        
        if note:
            return jsonify({'note': note, 'status': 'success'})
        else:
            return jsonify({'error': 'Note not found'}), 404
    except Exception as e:
        print(f"Error getting note: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update an existing note"""
    try:
        if not notes_db:
            return jsonify({'error': 'Notes database not available'}), 503
        
        data = request.json
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        
        success = notes_db.update_note(note_id, title, content, category)
        
        if success:
            return jsonify({
                'message': 'Note updated successfully',
                'status': 'success'
            })
        else:
            return jsonify({'error': 'Note not found'}), 404
    except Exception as e:
        print(f"Error updating note: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note"""
    try:
        if not notes_db:
            return jsonify({'error': 'Notes database not available'}), 503
        
        success = notes_db.delete_note(note_id)
        
        if success:
            return jsonify({
                'message': 'Note deleted successfully',
                'status': 'success'
            })
        else:
            return jsonify({'error': 'Note not found'}), 404
    except Exception as e:
        print(f"Error deleting note: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/notes/search', methods=['GET'])
def search_notes():
    """Search notes by query"""
    try:
        if not notes_db:
            return jsonify({'error': 'Notes database not available'}), 503
        
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        notes = notes_db.search_notes(query)
        
        return jsonify({
            'notes': notes,
            'query': query,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error searching notes: {e}")
        return jsonify({'error': str(e)}), 500

# ============= TODO API ENDPOINTS =============

@app.route('/todos', methods=['GET'])
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


# ============= CALENDAR API ENDPOINTS =============

@app.route('/events', methods=['GET'])
def get_events():
    """Get all events or upcoming events"""
    try:
        if not calendar_db:
            return jsonify({'error': 'Calendar database not available'}), 503
        
        # Check if requesting upcoming only
        upcoming_only = request.args.get('upcoming', 'false').lower() == 'true'
        
        if upcoming_only:
            events = calendar_db.get_upcoming_events(limit=20)
        else:
            events = calendar_db.get_all_events()
        
        return jsonify({'events': events, 'status': 'success'})
    except Exception as e:
        print(f"Error getting events: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/events', methods=['POST'])
def create_event():
    """Create a new event"""
    try:
        if not calendar_db:
            return jsonify({'error': 'Calendar database not available'}), 503
        
        data = request.json
        title = data.get('title', 'Untitled Event')
        description = data.get('description', '')
        event_date = data.get('event_date')
        event_time = data.get('event_time')
        duration = data.get('duration', 60)
        category = data.get('category', 'Study')
        
        if not event_date:
            return jsonify({'error': 'Event date is required'}), 400
        
        event_id = calendar_db.create_event(title, event_date, event_time, description, duration, category)
        
        return jsonify({
            'message': 'Event created successfully',
            'event_id': event_id,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error creating event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event by ID"""
    try:
        if not calendar_db:
            return jsonify({'error': 'Calendar database not available'}), 503
        
        event = calendar_db.get_event_by_id(event_id)
        
        if event:
            return jsonify({'event': event, 'status': 'success'})
        else:
            return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        print(f"Error getting event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an existing event"""
    try:
        if not calendar_db:
            return jsonify({'error': 'Calendar database not available'}), 503
        
        data = request.json
        title = data.get('title')
        description = data.get('description')
        event_date = data.get('event_date')
        event_time = data.get('event_time')
        duration = data.get('duration')
        category = data.get('category')
        
        success = calendar_db.update_event(event_id, title, description, event_date, event_time, duration, category)
        
        if success:
            return jsonify({
                'message': 'Event updated successfully',
                'status': 'success'
            })
        else:
            return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        print(f"Error updating event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/events/<int:event_id>/toggle', methods=['POST'])
def toggle_event_completed(event_id):
    """Toggle event completed status"""
    try:
        if not calendar_db:
            return jsonify({'error': 'Calendar database not available'}), 503
        
        success = calendar_db.toggle_completed(event_id)
        
        if success:
            return jsonify({
                'message': 'Event status toggled',
                'status': 'success'
            })
        else:
            return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        print(f"Error toggling event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event"""
    try:
        if not calendar_db:
            return jsonify({'error': 'Calendar database not available'}), 503
        
        success = calendar_db.delete_event(event_id)
        
        if success:
            return jsonify({
                'message': 'Event deleted successfully',
                'status': 'success'
            })
        else:
            return jsonify({'error': 'Event not found'}), 404
    except Exception as e:
        print(f"Error deleting event: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/events/date/<date>', methods=['GET'])
def get_events_by_date(date):
    """Get events for a specific date"""
    try:
        if not calendar_db:
            return jsonify({'error': 'Calendar database not available'}), 503
        
        events = calendar_db.get_events_by_date(date)
        
        return jsonify({
            'events': events,
            'date': date,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error getting events by date: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🤖 Starting Jarvis...")
    print(f"📍 Ollama URL: http://localhost:11434")
    print(f"🌐 Server running at: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
