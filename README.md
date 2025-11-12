# 🔮 Nexus - AI-Powered Study Assistant

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![Ollama](https://img.shields.io/badge/Ollama-LLaMA_3.2-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Nexus** is a comprehensive AI-powered study assistant built with Flask and powered by Ollama's LLaMA 3.2. It combines intelligent chat capabilities with productivity tools to enhance your learning experience.

---

## ✨ Features

### 🤖 AI Chat Assistant
- **Intelligent Conversations**: Powered by Ollama (LLaMA 3.2) for natural, context-aware responses
- **Document-Aware**: Upload PDFs and text files for context-based Q&A
- **Study Tools**: Quick actions for Summarize, Flashcards, and Explain
- **Full-Width Messages**: Clean, readable chat interface with glass morphism design

![Chat Interface](https://raw.githubusercontent.com/deimon999/GigaRepose/main/screenshots/chat.png)

### 📝 Notes Manager
- **Rich Note Taking**: Create, edit, and organize study notes
- **Categories & Tags**: Organize notes by subject and topic
- **Search Functionality**: Quickly find notes with built-in search
- **Date Tracking**: Automatic timestamps for created and updated notes

![Notes Manager](https://raw.githubusercontent.com/deimon999/GigaRepose/main/screenshots/notes.png)

### ✅ To-Do List
- **Task Management**: Add, complete, and delete tasks
- **Priority Levels**: High, Medium, Low priority tags
- **Due Dates**: Set deadlines for your tasks
- **Progress Tracking**: See pending vs completed tasks at a glance

![To-Do List](https://raw.githubusercontent.com/deimon999/GigaRepose/main/screenshots/todos.png)

### ⏱️ Pomodoro Timer
- **Focus Sessions**: 25-minute work sessions with 5-minute breaks
- **Visual Progress**: Circular timer with real-time countdown
- **Session Tracking**: Monitor daily sessions and total minutes
- **Task Association**: Link pomodoro sessions to specific tasks

![Pomodoro Timer](https://raw.githubusercontent.com/deimon999/GigaRepose/main/screenshots/pomodoro.png)

### � Bookmarks Manager
- **URL Storage**: Save important study resources and references
- **Categories**: Organize bookmarks by subject or type
- **Tags**: Add multiple tags for flexible organization
- **Descriptions**: Add notes about each bookmark

![Bookmarks Manager](https://raw.githubusercontent.com/deimon999/GigaRepose/main/screenshots/bookmarks.png)

### 📄 Document Manager
- **File Upload**: Support for PDF and TXT files
- **Document Search**: RAG-based retrieval for intelligent Q&A
- **Drag & Drop**: Easy file upload interface
- **Document Ingestion**: Process documents for AI context

![Document Manager](https://raw.githubusercontent.com/deimon999/GigaRepose/main/screenshots/documents.png)

### 🏠 Full Application View
- **Responsive Layout**: Sidebar navigation + main chat area + feature panels
- **Glass Morphism UI**: Modern, sleek design with blur effects
- **Dark Theme**: Easy on the eyes for long study sessions
- **Smooth Animations**: Polished transitions and interactions

![Home View](https://raw.githubusercontent.com/deimon999/GigaRepose/main/screenshots/home.png)

---

## 🛠️ Tech Stack

### Backend
- **Flask 3.0.0** - Python web framework
- **SQLite** - Lightweight database for notes, todos, bookmarks, pomodoro sessions
- **Ollama** - Local LLM inference (LLaMA 3.2)
- **LangChain** - LLM orchestration and retrieval (optional)

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Glass morphism, animations, responsive design
- **HTML5** - Semantic markup

### Features & Performance
- **Database Indexing** - Optimized queries with strategic indexes
- **Performance Monitoring** - Request timing and slow query logging
- **Event Debouncing** - Smooth UI with prevented duplicate actions
- **Modular Architecture** - Separate modules for each feature

---

## 📋 Prerequisites

Before running Nexus, ensure you have:

1. **Python 3.11+** installed
2. **Ollama** installed and running ([Download Ollama](https://ollama.ai))
3. **LLaMA 3.2 model** pulled in Ollama:
   ```bash
   ollama pull llama3.2
   ```

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/deimon999/GigaRepose.git
cd GigaRepose/jarvis-mvp
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Ollama (Optional)
If Ollama is not running on default `http://localhost:11434`, update the URL in `app.py`.

### 6. Enable Document Search (Optional)
To enable RAG-based document search with Pinecone:
```bash
set ENABLE_RETRIEVER=1  # Windows
export ENABLE_RETRIEVER=1  # Linux/Mac
```

---

## 🎯 Running the Application

### Start the Server
```bash
cd jarvis-mvp
python app.py
```

### Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

### Expected Output
```
✓ Connected to Ollama at http://localhost:11434
✓ LLM client initialized successfully
✓ Bookmarks database initialized: jarvis_bookmarks.db
✓ Pomodoro database initialized: jarvis_pomodoro.db
✓ Notes database initialized: jarvis_notes.db
✓ Todo database initialized: jarvis_todos.db
ℹ Document search disabled (set ENABLE_RETRIEVER=1 to enable)
✓ Document manager initialized successfully
🔮 Starting Nexus...
🤖 Ollama URL: http://localhost:11434
🌐 Server running at: http://localhost:5000
```

---

## 📁 Project Structure

```
jarvis-mvp/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── PERFORMANCE_OPTIMIZATIONS.md  # Performance improvements documentation
├── app/
│   ├── __init__.py
│   ├── llm_client.py          # Ollama LLM integration
│   ├── notes_db.py            # Notes database operations
│   ├── todo_db.py             # Todo database operations
│   ├── pomodoro_db.py         # Pomodoro session tracking
│   ├── bookmarks_db.py        # Bookmarks storage
│   ├── document_manager.py    # Document upload handling
│   ├── retriever.py           # RAG retrieval (optional)
│   └── ingest.py              # Document ingestion (optional)
├── static/
│   ├── css/
│   │   └── style.css          # Main stylesheet (glass morphism)
│   └── js/
│       ├── app.js             # Main app logic & navigation
│       ├── notes.js           # Notes feature
│       ├── todos.js           # To-Do feature
│       ├── pomodoro.js        # Pomodoro timer
│       ├── bookmarks.js       # Bookmarks feature
│       ├── documents.js       # Document management
│       └── modals.js          # Modal dialogs
├── templates/
│   └── index.html             # Main HTML template
└── data/
    ├── documents.json         # Document metadata
    ├── jarvis_notes.db        # SQLite notes database
    ├── jarvis_todos.db        # SQLite todos database
    ├── jarvis_pomodoro.db     # SQLite pomodoro database
    └── jarvis_bookmarks.db    # SQLite bookmarks database
```

---

## 🎨 UI/UX Features

- **Glass Morphism Design**: Modern frosted glass effect with blur
- **Smooth Animations**: Fade-ins, slide-ins, and transitions
- **Responsive Panels**: Slide-out panels for each feature
- **Dark Theme**: Optimized for long study sessions
- **Full-Width Messages**: Clean chat interface without avatars
- **Debounced Navigation**: Smooth transitions without flickering

---

## 🔧 Configuration

### Environment Variables
- `ENABLE_RETRIEVER=1` - Enable document search with Pinecone
- `OLLAMA_URL` - Custom Ollama endpoint (default: `http://localhost:11434`)

### Customization
- **LLM Model**: Change in `app/llm_client.py` (default: `llama3.2`)
- **Pomodoro Duration**: Modify in `static/js/pomodoro.js` (default: 25 min work, 5 min break)
- **Theme Colors**: Update CSS variables in `static/css/style.css`

---

## 🚀 Performance Optimizations

This project includes several performance enhancements:

✅ **Database Indexing**: Strategic indexes on frequently queried columns  
✅ **Request Monitoring**: Automatic logging of slow requests (>100ms)  
✅ **Event Debouncing**: Prevents duplicate event listeners and flickering  
✅ **Static File Caching**: 1-year cache for CSS/JS files  
✅ **Connection Pooling**: Optimized database connections  

See [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) for detailed analysis.

---

## 🐛 Troubleshooting

### Ollama Connection Failed
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

### Port Already in Use
```bash
# Change port in app.py
app.run(port=5001)  # Use different port
```

### Database Errors
```bash
# Delete databases to reset
rm jarvis_*.db
python app.py  # Will recreate fresh databases
```

### Browser Cache Issues
- Hard refresh: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- Or open in Incognito/Private mode

---

## 📝 Usage Tips

### Chat Features
- Type naturally - the AI understands context
- Upload documents first for document-based Q&A
- Use quick actions: Summarize, Flashcards, Explain

### Study Workflow
1. **Upload Documents** - Add your study materials
2. **Take Notes** - Jot down key points while reading
3. **Create Tasks** - Break down topics into actionable items
4. **Use Pomodoro** - Focus on tasks with timed sessions
5. **Save Resources** - Bookmark helpful websites
6. **Ask Questions** - Get AI explanations when stuck

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **LLaMA 3.2** - Meta's language model
- **Flask** - Python web framework
- **LangChain** - LLM orchestration (optional)

---

## 📧 Contact

**Project Maintainer**: deimon999  
**Repository**: [GigaRepose](https://github.com/deimon999/GigaRepose)

---

## 🗺️ Roadmap

- [ ] Calendar integration for scheduling
- [ ] Export notes as PDF/Markdown
- [ ] Mobile responsive design
- [ ] Voice input for chat
- [ ] Multi-language support
- [ ] Cloud sync for notes/bookmarks
- [ ] Browser extension for quick bookmarking
- [ ] Statistics and analytics dashboard

---

**Built with ❤️ by deimon999**
