# BOT GPT 🤖

A production-grade conversational AI backend platform with RAG (Retrieval-Augmented Generation) support.

**Author:** Himesh Parashar

---

## ✨ Features

- **Open Chat Mode** - General conversations with LLM
- **RAG Mode** - Document-grounded conversations (chat with PDFs)
- **Multi-LLM Support** - Gemini, Groq, OpenAI providers
- **Sliding Window Context** - Efficient token management
- **Full CRUD API** - Create, Read, Update, Delete conversations
- **Document Ingestion** - PDF/TXT upload with chunking & embeddings

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | PostgreSQL |
| Vector Store | ChromaDB |
| LLM | Gemini / Groq / OpenAI |
| Embeddings | Google Gemini |
| Containerization | Docker |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- API Key (Gemini, Groq, or OpenAI)

### 1. Clone & Setup

```bash
git clone https://github.com/himeshparashar/bot_gpt.git
cd bot_gpt
```

### 2. Configure Environment

```bash
# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=your_gemini_api_key
# Optional: GROQ_API_KEY=your_groq_key
# Optional: OPENAI_API_KEY=your_openai_key
EOF
```

### 3. Run with Docker

```bash
docker compose up --build
```

### 4. Access API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 📡 API Endpoints

### Conversations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/conversations` | Create conversation with first message |
| `GET` | `/api/v1/conversations?user_id=` | List user's conversations |
| `GET` | `/api/v1/conversations/{id}` | Get conversation details |
| `POST` | `/api/v1/conversations/{id}/messages` | Add message (continue chat) |
| `DELETE` | `/api/v1/conversations/{id}` | Delete conversation |

### Documents (RAG)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents/upload` | Upload document for RAG |
| `DELETE` | `/api/v1/documents/{id}` | Delete document |

---

## 💬 Usage Examples

### Create a Conversation

```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "message": "Hello! What can you help me with?",
    "mode": "open_chat"
  }'
```

### Continue Conversation

```bash
curl -X POST http://localhost:8000/api/v1/conversations/{conversation_id}/messages \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Python programming"
  }'
```

### Upload Document for RAG

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@document.pdf"
```

---

## 🏗️ Project Structure

```
bot_gpt/
├── app/
│   ├── main.py              # FastAPI app
│   ├── api/v1/endpoints/    # API routes
│   ├── core/                # Config, database, exceptions
│   ├── models/              # SQLAlchemy models
│   ├── repositories/        # Data access layer
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic
│       ├── llm/             # LLM providers
│       ├── embeddings/      # Embedding providers
│       └── vectorstore/     # Vector store
├── tests/                   # Unit tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🧪 Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | - | Gemini API key |
| `GROQ_API_KEY` | - | Groq API key (optional) |
| `OPENAI_API_KEY` | - | OpenAI API key (optional) |
| `DEFAULT_LLM_PROVIDER` | `gemini` | LLM provider to use |
| `MAX_CONTEXT_TOKENS` | `4096` | Max context window |
| `SLIDING_WINDOW_MESSAGES` | `20` | Max messages in context |

---

## 🔑 Key Design Decisions

1. **Sliding Window Context** - Keeps last N messages within token budget
2. **Strategy Pattern** - Swappable LLM/Embedding providers
3. **Repository Pattern** - Clean data access abstraction
4. **Sequence-based Ordering** - Reliable message ordering

---


**Built with ❤️ by Himesh Parashar**
