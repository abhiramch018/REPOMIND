# 🧠 RepoMind — AI-Powered GitHub Repository Analyzer

Analyze any GitHub repository and ask AI-powered questions about the codebase using RAG (Retrieval-Augmented Generation).

![RepoMind Screenshot](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal)

## ✨ Features

- 🔍 **Code Search** — Semantic search across the entire codebase
- 🏗️ **Architecture Analysis** — Understand project structure and design patterns
- 🐛 **Debug Help** — Get AI-powered debugging suggestions
- 📖 **Code Explanations** — Natural language explanations of complex code

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, FastAPI, Uvicorn |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | FAISS |
| LLM | Google Gemini API |
| Git Operations | GitPython |
| Frontend | HTML, CSS, JavaScript |

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/RepoMind.git
cd RepoMind
```

### 2. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Set up your API key
```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your Google Gemini API key
```

Get your free API key at [Google AI Studio](https://aistudio.google.com/apikeys).

### 4. Run the server
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Open the app
Navigate to **http://localhost:8000** in your browser.

## 📖 How It Works

1. **Paste** a GitHub repository URL and click **Analyze**
2. The system clones the repo, extracts code files, and generates semantic embeddings
3. Embeddings are stored in a FAISS vector index for fast similarity search
4. **Ask** any question about the codebase
5. Relevant code snippets are retrieved via semantic search and sent to Google Gemini
6. The AI responds with detailed explanations, referencing specific files

## 📁 Project Structure

```
RepoMind/
├── backend/
│   ├── main.py           # FastAPI app with /analyze and /ask endpoints
│   ├── config.py          # Shared settings & constants
│   ├── cloner.py          # GitPython repo cloner
│   ├── scanner.py         # Recursive code file extractor
│   ├── embedder.py        # Embedding generation & chunking
│   ├── vector_store.py    # FAISS index management
│   ├── llm.py             # Google Gemini API integration
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # API key template
├── frontend/
│   ├── index.html         # Chat interface
│   ├── style.css          # Premium dark theme
│   └── script.js          # Frontend logic
└── data/                  # Runtime data (auto-generated)
```

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Clone & index a GitHub repository |
| `POST` | `/ask` | Ask a question about an analyzed repo |
| `GET` | `/health` | Health check |

## 📄 License

MIT License
