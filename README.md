# Jarvis MVP - Personal AI Assistant

A Flask-based personal AI assistant with document management, notes, todos, and calendar features powered by Ollama and Pinecone.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 🤖 **AI Chat** - Powered by Ollama (llama3.2:latest) for intelligent conversations
- � **Document Management** - Upload, store, and manage PDF/TXT documents
- � **Notes System** - Create, edit, and organize personal notes
- ✅ **Todo List** - Task management with SQLite database
- � **Calendar** - Event tracking and scheduling
- 🔍 **Semantic Search** - Vector-based document search with Pinecone (optional)

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** installed
- **Ollama** - Download from [ollama.ai](https://ollama.ai)
- **Pinecone API Key** (optional) - Get free key from [pinecone.io](https://www.pinecone.io)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/deimon999/GigaRepose.git
cd GigaRepose
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Create a `.env` file in the project root:
```env
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=gcp-starter
```

4. **Install and start Ollama**

Download Ollama from [ollama.ai](https://ollama.ai), then:
```bash
# Pull the required model
ollama pull llama3.2:latest

# Start Ollama server (runs automatically on most systems)
ollama serve
```

5. **Run the application**
```bash
python app.py
```

6. **Open your browser**

Visit `http://localhost:5000` and start using Jarvis!

## 📁 Project Structure

```
jarvis-mvp/
├── app.py                    # Main Flask application & API routes
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── .gitignore               # Git ignore rules
├── KNOWLEDGE_BASE.md        # Project documentation
├── app/
│   ├── __init__.py
│   ├── llm_client.py        # Ollama LLM client integration
│   ├── retriever.py         # Pinecone vector search
│   ├── ingest.py            # Document ingestion to Pinecone
│   ├── notes_db.py          # SQLite notes database handler
│   ├── calendar_db.py       # SQLite calendar database handler
│   ├── todo_db.py           # SQLite todo database handler
│   └── document_manager.py  # Document upload & management
├── data/
│   └── documents.json       # Document metadata storage
├── static/
│   ├── css/
│   │   └── style.css        # Application styles
│   └── js/
│       ├── app.js           # Main chat interface
│       ├── documents.js     # Document management UI
│       ├── notes.js         # Notes UI
│       ├── todos.js         # Todos UI
│       └── calendar.js      # Calendar UI
└── templates/
    └── index.html           # Main application template
```

## 🎯 Usage Guide

### 💬 Chat with Jarvis
1. Type your message in the chat input at the bottom
2. Press Enter or click Send
3. Jarvis will respond using Ollama AI
4. Chat history is maintained during your session

### 📝 Managing Notes
- Click "Notes" tab
- Click "New Note" to create
- Fill in title and content
- Save or cancel
- Edit or delete existing notes

### ✅ Managing Todos
- Click "Todos" tab
- Click "Add Todo" 
- Enter task description and priority
- Mark tasks complete with checkbox
- Delete completed tasks

### 📄 Document Management
- Click "Documents" tab
- Click "Upload Document" to add PDFs or TXT files
- View all uploaded documents
- Delete documents you no longer need
- Click "Re-index All Documents" to update search index

### 📅 Calendar (Coming Soon)
- Schedule events and study sessions
- Track important dates
- View monthly calendar

## ⚙️ Configuration

### Document Search (Optional)

By default, document semantic search is **disabled** due to Windows compatibility issues with TensorFlow/sentence-transformers.

To enable document search:

**Windows:**
```powershell
$env:ENABLE_RETRIEVER="1"
python app.py
```

**Linux/Mac:**
```bash
export ENABLE_RETRIEVER=1
python app.py
```

**Note:** This requires:
- Valid Pinecone API key in `.env`
- sentence-transformers library (may have issues on Windows)
- Documents ingested to Pinecone

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PINECONE_API_KEY` | Optional | Your Pinecone API key for vector search |
| `PINECONE_ENV` | Optional | Pinecone environment (default: gcp-starter) |
| `ENABLE_RETRIEVER` | Optional | Set to "1" to enable document search |

## 🔧 API Endpoints

### Chat
- `POST /chat` - Send message to AI
  - Body: `{ "message": "your message" }`
  - Returns: `{ "response": "AI response" }`

### Notes
- `GET /notes` - Get all notes
- `POST /notes` - Create new note
  - Body: `{ "title": "...", "content": "..." }`
- `PUT /notes/<id>` - Update note
- `DELETE /notes/<id>` - Delete note

### Todos
- `GET /todos` - Get all todos
- `POST /todos` - Create new todo
  - Body: `{ "task": "...", "priority": "high|medium|low" }`
- `PUT /todos/<id>` - Update todo
- `DELETE /todos/<id>` - Delete todo

### Documents
- `GET /documents` - List all documents
- `POST /upload` - Upload document (multipart/form-data)
- `DELETE /documents/<id>` - Delete document
- `POST /ingest-all` - Re-index all documents to Pinecone

### Calendar
- `GET /events` - Get all events
- `POST /events` - Create new event
- `PUT /events/<id>` - Update event
- `DELETE /events/<id>` - Delete event

## 🛠️ Technologies

| Category | Technology |
|----------|-----------|
| **Backend** | Flask 3.0.0, Python 3.10+ |
| **Database** | SQLite (notes, calendar, todos) |
| **Vector Store** | Pinecone 7.3.0 (optional) |
| **LLM** | Ollama (llama3.2:latest) |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Document Processing** | langchain-community, pypdf |
| **Frontend** | Vanilla JavaScript, CSS |

## 🐛 Troubleshooting

### "Could not connect to Ollama"
- Ensure Ollama is running: `ollama serve`
- Check if model exists: `ollama list`
- Pull model if missing: `ollama pull llama3.2:latest`
- Verify Ollama is on `http://localhost:11434`

### "Document indexing is disabled"
- This is normal - document search is disabled by default
- To enable, set `ENABLE_RETRIEVER=1` environment variable
- Ensure Pinecone API key is in `.env` file

### Import/Dependency Errors
```bash
pip install -r requirements.txt --upgrade
```

### Database Issues
- Delete `.db` files to reset databases
- They will be recreated on next startup

### Port Already in Use
```bash
# Change port in app.py or kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - feel free to use and modify!

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [Pinecone](https://www.pinecone.io/) for vector database
- [Flask](https://flask.palletsprojects.com/) for web framework
- [LangChain](https://www.langchain.com/) for document processing

---

**Made with ❤️ for productivity and learning**
