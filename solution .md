# BOT GPT - Solution Document

## 🎯 Executive Summary

BOT GPT is a production-grade conversational AI backend platform built with FastAPI, PostgreSQL, and multiple LLM provider integrations. The system supports both **Open Chat Mode** (general conversations) and **RAG Mode** (Retrieval-Augmented Generation for document-grounded conversations), with a clean architecture following SOLID principles and industry best practices.

---

## 📐 Architecture & Design

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│                    (Postman / cURL / Swagger UI / Frontend)                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               API LAYER                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     FastAPI Application                              │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │    │
│  │  │  /conversations  │  │   /documents     │  │     /health      │  │    │
│  │  │     Router       │  │     Router       │  │     Endpoint     │  │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             SERVICE LAYER                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  ChatService    │  │ IngestionService│  │     ContextManager          │  │
│  │  - Orchestrates │  │ - Document      │  │     - Sliding Window        │  │
│  │    conversations│  │   processing    │  │     - Token Counting        │  │
│  │  - LLM calls    │  │ - Chunking      │  │     - Context Building      │  │
│  └─────────────────┘  │ - Embedding     │  └─────────────────────────────┘  │
│           │           └─────────────────┘              │                     │
│           │                    │                       │                     │
│  ┌────────▼────────────────────▼───────────────────────▼─────────────────┐  │
│  │                    LLM Provider Layer (Strategy Pattern)              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │  │
│  │  │   Gemini     │  │    Groq      │  │   OpenAI     │                │  │
│  │  │   Provider   │  │   Provider   │  │   Provider   │                │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    Embedding & Vector Store Layer                     │  │
│  │  ┌──────────────────────┐        ┌──────────────────────┐            │  │
│  │  │  Gemini Embeddings   │   ───▶ │   ChromaDB Vector    │            │  │
│  │  │  (768 dimensions)    │        │   Store (Persistent) │            │  │
│  │  └──────────────────────┘        └──────────────────────┘            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           REPOSITORY LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              ConversationRepository / MessageRepository              │    │
│  │                    (CRUD Operations + Custom Queries)                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PERSISTENCE LAYER                                   │
│  ┌───────────────────────────────┐  ┌───────────────────────────────────┐   │
│  │       PostgreSQL Database     │  │      ChromaDB (Vector Store)      │   │
│  │  - Conversations              │  │  - Document Embeddings            │   │
│  │  - Messages                   │  │  - Semantic Search                │   │
│  │  - Documents                  │  │  - Persistent Storage             │   │
│  └───────────────────────────────┘  └───────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Tech Stack Justification

| Component | Technology | Justification |
|-----------|------------|---------------|
| **API Framework** | FastAPI | Async support, automatic OpenAPI docs, type hints, high performance |
| **Database** | PostgreSQL | ACID compliance, robust for production, excellent for relational data |
| **ORM** | SQLAlchemy | Mature, flexible, supports async operations |
| **Vector Store** | ChromaDB | Persistent embeddings, easy integration, suitable for RAG |
| **LLM Integration** | LangChain | Unified interface, multiple provider support, streaming |
| **LLM Providers** | Gemini, Groq, OpenAI | Free tier availability (Gemini/Groq), flexibility |
| **Embeddings** | Google Gemini | Free tier, 768-dimension vectors, good quality |
| **Containerization** | Docker + Docker Compose | Easy deployment, consistent environments |
| **CI/CD** | GitHub Actions | Integrated with GitHub, comprehensive pipeline |

---

## 📊 Data & Storage Design

### Database Choice: PostgreSQL

**Why PostgreSQL?**
1. **ACID Compliance**: Ensures data integrity for conversation history
2. **Relational Model**: Natural fit for User → Conversation → Message hierarchy
3. **Scalability**: Supports horizontal scaling, replication, and sharding
4. **JSON Support**: Can store metadata as JSONB if needed
5. **Production Ready**: Battle-tested for enterprise applications

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       CONVERSATIONS                              │
├─────────────────────────────────────────────────────────────────┤
│ id            : UUID (PK)                                       │
│ user_id       : VARCHAR (Indexed)                               │
│ title         : VARCHAR(255)                                    │
│ mode          : ENUM (open_chat, rag)                           │
│ total_tokens  : INTEGER (Token usage tracking)                  │
│ is_active     : BOOLEAN                                         │
│ created_at    : TIMESTAMP                                       │
│ updated_at    : TIMESTAMP                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         MESSAGES                                 │
├─────────────────────────────────────────────────────────────────┤
│ id              : UUID (PK)                                     │
│ conversation_id : UUID (FK → conversations.id, CASCADE DELETE)  │
│ role            : ENUM (user, assistant, system)                │
│ content         : TEXT                                          │
│ sequence_number : INTEGER (Indexed - ensures ordering)          │
│ token_count     : INTEGER (Per-message token tracking)          │
│ is_summary      : BOOLEAN (For future summarization support)    │
│ created_at      : TIMESTAMP                                     │
│ updated_at      : TIMESTAMP                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         DOCUMENTS                                │
├─────────────────────────────────────────────────────────────────┤
│ id          : UUID (PK)                                         │
│ filename    : VARCHAR(255)                                      │
│ content     : TEXT                                              │
│ chunk_count : INTEGER                                           │
│ status      : VARCHAR(50) (pending, completed, failed)          │
│ created_at  : TIMESTAMP                                         │
│ updated_at  : TIMESTAMP                                         │
└─────────────────────────────────────────────────────────────────┘
```

### Message Ordering Strategy

Messages are ordered using a `sequence_number` column:
- **Auto-incrementing per conversation**: Each new message gets `MAX(sequence_number) + 1`
- **Indexed for performance**: Fast retrieval of ordered messages
- **Reliable ordering**: More robust than timestamp-based ordering

```python
def get_next_sequence_number(self, db: Session, conversation_id: str) -> int:
    result = db.query(func.max(Message.sequence_number)).filter(
        Message.conversation_id == conversation_id
    ).scalar()
    return (result or 0) + 1
```

### Token Usage Tracking

- **Per-message tracking**: `token_count` stored on each message
- **Conversation-level aggregation**: `total_tokens` on conversation for quick access
- **Cost monitoring**: Enables usage analytics and cost management

---

## 🔌 REST API Design

### Base URL: `/api/v1`

### Conversations API

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `POST` | `/conversations` | Create new conversation with first message | `CreateConversationRequest` | `201 Created` |
| `GET` | `/conversations?user_id=&skip=&limit=` | List user's conversations (paginated) | Query params | `200 OK` |
| `GET` | `/conversations/{id}` | Get conversation with all messages | Path param | `200 OK` |
| `GET` | `/conversations/{id}/messages` | Get messages (paginated) | Path + Query | `200 OK` |
| `POST` | `/conversations/{id}/messages` | Add message & get AI response | `AddMessageRequest` | `201 Created` |
| `DELETE` | `/conversations/{id}` | Delete conversation & messages | Path param | `204 No Content` |

### Documents API

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `POST` | `/documents/upload` | Upload document for RAG | `multipart/form-data` | `200 OK` |
| `DELETE` | `/documents/{id}` | Delete document from vector store | Path param | `200 OK` |

### Request/Response Schemas

#### Create Conversation
```json
// POST /api/v1/conversations
// Request
{
  "user_id": "user-123",
  "message": "Hello, how can you help me today?",
  "title": "Getting Started",  // optional
  "mode": "open_chat"  // or "rag"
}

// Response (201 Created)
{
  "conversation_id": "uuid-here",
  "title": "Getting Started",
  "user_message": {
    "id": "msg-uuid",
    "role": "user",
    "content": "Hello, how can you help me today?",
    "sequence_number": 1,
    "token_count": 8,
    "is_summary": false,
    "created_at": "2025-11-30T10:00:00Z"
  },
  "assistant_message": {
    "id": "msg-uuid-2",
    "role": "assistant",
    "content": "Hello! I'm BOT GPT...",
    "sequence_number": 2,
    "token_count": 45,
    "is_summary": false,
    "created_at": "2025-11-30T10:00:01Z"
  }
}
```

#### Add Message to Conversation
```json
// POST /api/v1/conversations/{id}/messages
// Request
{
  "message": "What is the capital of France?"
}

// Response (201 Created)
{
  "conversation_id": "uuid-here",
  "user_message": { ... },
  "assistant_message": { ... }
}
```

#### List Conversations (Paginated)
```json
// GET /api/v1/conversations?user_id=user-123&skip=0&limit=20
// Response (200 OK)
{
  "items": [
    {
      "id": "uuid",
      "user_id": "user-123",
      "title": "Getting Started",
      "mode": "open_chat",
      "total_tokens": 150,
      "is_active": true,
      "message_count": 6,
      "last_message_preview": "The capital of France is Paris...",
      "created_at": "2025-11-30T10:00:00Z",
      "updated_at": "2025-11-30T10:05:00Z"
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 20,
  "has_more": false
}
```

### HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| `200` | OK | Successful GET, successful document operations |
| `201` | Created | New conversation or message created |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Invalid input, chat errors |
| `404` | Not Found | Conversation/resource not found |
| `422` | Unprocessable Entity | Document processing errors |
| `503` | Service Unavailable | LLM provider errors |

---

## 🧠 LLM Context & Cost Management

### Context Construction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT BUILDING PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. Calculate Available Token Budget                             │
│    available = MAX_CONTEXT_TOKENS - MAX_RESPONSE_TOKENS         │
│    (4096 - 1024 = 3072 tokens available)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Add System Prompt (Mode-Specific)                            │
│    - Open Chat: General assistant prompt                        │
│    - RAG: Document-grounded prompt + retrieved context          │
│    Budget: ~500 tokens                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Apply Sliding Window Strategy                                │
│    - Take last N messages (default: 20)                         │
│    - Iterate from newest to oldest                              │
│    - Add messages until token limit reached                     │
│    - Maintain chronological order in final context              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Final Context = [System] + [Recent Messages within budget]   │
└─────────────────────────────────────────────────────────────────┘
```

### Sliding Window Implementation

```python
def _apply_sliding_window(self, messages: List[Dict], max_tokens: int) -> List[Dict]:
    """Keep most recent messages within token limit"""
    # 1. Limit to max sliding window size (default: 20 messages)
    recent_messages = messages[-self.config.sliding_window_messages:]
    
    selected = []
    current_tokens = 0
    
    # 2. Iterate from newest to oldest
    for message in reversed(recent_messages):
        message_tokens = self.token_counter.count_messages_tokens([message])
        
        # 3. Add if within budget
        if current_tokens + message_tokens <= max_tokens:
            selected.insert(0, message)  # Maintain chronological order
            current_tokens += message_tokens
        else:
            break
    
    return selected
```

### Token Counting Strategy

Two implementations available:
1. **TiktokenCounter**: Accurate counting using OpenAI's tiktoken library
2. **SimpleTokenCounter**: Fallback using `len(text) // 4` approximation

```python
class TiktokenCounter(TokenCounterStrategy):
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.encoding = tiktoken.encoding_for_model(model)
        self.tokens_per_message = 4  # Overhead per message
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))
```

### Cost Optimization Strategies

| Strategy | Implementation | Benefit |
|----------|----------------|---------|
| **Sliding Window** | Keep last 20 messages max | Bounds context size |
| **Token Budget** | Reserve 1024 tokens for response | Prevents overflow |
| **Per-Message Tracking** | Store `token_count` per message | Fast context building |
| **System Prompt Budget** | 500 token limit for system prompts | Predictable overhead |
| **Free-Tier LLMs** | Gemini Flash, Groq | Zero cost for development |

### Configuration Settings

```python
# Context Management Settings
MAX_CONTEXT_TOKENS: int = 4096      # Total context window
MAX_RESPONSE_TOKENS: int = 1024     # Reserved for response
SLIDING_WINDOW_MESSAGES: int = 20   # Max messages in window
SYSTEM_PROMPT_TOKEN_BUDGET: int = 500  # System prompt limit
```

---

## 📚 RAG (Retrieval-Augmented Generation) Design

### RAG Pipeline Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    DOCUMENT INGESTION FLOW                     │
└───────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │              Upload Document               │
        │         (PDF, TXT, Markdown)              │
        └─────────────────────┬─────────────────────┘
                              │
        ┌─────────────────────▼─────────────────────┐
        │           DocumentProcessor               │
        │    - Extract text from PDF (PyPDFLoader) │
        │    - Decode text files                   │
        └─────────────────────┬─────────────────────┘
                              │
        ┌─────────────────────▼─────────────────────┐
        │              TextChunker                  │
        │    - RecursiveCharacterTextSplitter      │
        │    - chunk_size: 1000, overlap: 200      │
        └─────────────────────┬─────────────────────┘
                              │
        ┌─────────────────────▼─────────────────────┐
        │         Embedding Generation              │
        │    - Gemini Embeddings (768 dimensions)  │
        │    - Batch processing                     │
        └─────────────────────┬─────────────────────┘
                              │
        ┌─────────────────────▼─────────────────────┐
        │          ChromaDB Vector Store            │
        │    - Persistent storage                   │
        │    - Cosine similarity search            │
        └───────────────────────────────────────────┘
```

### Chunking Strategy

```python
class TextChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,  # Track position in original doc
        )
```

- **Chunk Size**: 1000 characters (optimal for semantic coherence)
- **Overlap**: 200 characters (maintains context across chunks)
- **Position Tracking**: Stores start index for reference

### Vector Store Implementation

```python
class ChromaVectorStore(BaseVectorStore):
    async def add_documents(self, chunks: List[DocumentChunk]) -> List[str]:
        self._collection.add(
            ids=[chunk.id for chunk in chunks],
            embeddings=[chunk.embedding for chunk in chunks],
            documents=[chunk.content for chunk in chunks],
            metadatas=[chunk.metadata for chunk in chunks]
        )
    
    async def search(self, query_embedding: List[float], top_k: int = 5):
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
```

### RAG Mode System Prompt

```python
class RAGPrompt(BasePromptTemplate):
    def get_system_prompt(self, document_context: str = "", **kwargs) -> str:
        return f"""You are BOT GPT operating in Document-Grounded Mode.

Guidelines:
1. Prioritize information from the provided document context
2. If the context doesn't contain the answer, clearly state that
3. Quote or reference specific parts of the documents when relevant

Document Context:
---
{document_context}
---
Use the above context to answer user questions accurately."""
```

---

## ⚠️ Error Handling & Scalability

### Custom Exception Hierarchy

```python
class ChatException(HTTPException):
    """Chat-related errors (400 Bad Request)"""
    
class LLMException(HTTPException):
    """LLM provider errors (503 Service Unavailable)"""
    
class DocumentException(HTTPException):
    """Document processing errors (422 Unprocessable Entity)"""
```

### Error Handling Patterns

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING FLOW                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  LLM API Timeout │ -> │  LLMException    │ -> │  503 Response    │
│                  │    │  (Retry-able)    │    │  + Error Details │
└──────────────────┘    └──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  DB Write Fail   │ -> │  SQLAlchemy      │ -> │  500 Response    │
│                  │    │  Rollback        │    │  + Transaction   │
└──────────────────┘    └──────────────────┘    └──────────────────┘

┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Token Limit     │ -> │  Context Manager │ -> │  Sliding Window  │
│  Exceeded        │    │  Auto-Truncate   │    │  Applied         │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

### Endpoint Error Handling Example

```python
@router.post("/{conversation_id}/messages")
async def add_message(conversation_id: str, request: AddMessageRequest, ...):
    try:
        response = await service.add_message(db, conversation_id, request)
        return response
    except ChatException as e:
        if "not found" in str(e.detail).lower():
            raise HTTPException(status_code=404, detail=str(e.detail))
        raise HTTPException(status_code=400, detail=str(e.detail))
    except LLMException as e:
        raise HTTPException(status_code=503, detail=str(e.detail))
```

### Scalability Analysis

#### Bottleneck Identification at 1M Users

| Layer | Bottleneck | Solution |
|-------|------------|----------|
| **API** | Connection handling | Horizontal scaling with load balancer |
| **Database** | Read/write throughput | Read replicas, connection pooling |
| **LLM API** | Rate limits, latency | Request queuing, provider failover |
| **Vector Store** | Search latency | Sharding, dedicated vector DB (Pinecone) |

#### Scaling Strategies

```
┌─────────────────────────────────────────────────────────────────┐
│                    HORIZONTAL SCALING                            │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │   Load Balancer  │
                    └────────┬─────────┘
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
    │  API Pod 1  │   │  API Pod 2  │   │  API Pod N  │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
       ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
       │  Primary DB │ │  Replica  │ │   Redis     │
       │  (Write)    │ │  (Read)   │ │   Cache     │
       └─────────────┘ └───────────┘ └─────────────┘
```

#### Future Enhancements

1. **Redis Cache**: Cache frequent conversations, reduce DB load
2. **Message Queue**: Async LLM calls with RabbitMQ/Celery
3. **Database Sharding**: Partition by user_id for horizontal scaling
4. **Kubernetes**: Container orchestration for auto-scaling
5. **CDN**: Static asset delivery for frontend (if added)

---

## 🐳 Deployment & DevOps

### Docker Configuration

#### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### Docker Compose
```yaml
services:
  app:
    build: .
    container_name: bot_gpt_app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: bot_gpt
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d bot_gpt"]
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
jobs:
  lint:        # Code quality with Black, isort, flake8
  test:        # Unit tests with pytest + PostgreSQL service
  build:       # Docker image build and verification
  security:    # Dependency vulnerability scanning (safety)
  integration: # API health checks, endpoint verification
```

#### Pipeline Stages

| Stage | Tools | Purpose |
|-------|-------|---------|
| **Lint** | Black, isort, flake8 | Code formatting and style |
| **Test** | pytest, pytest-cov | Unit tests with coverage |
| **Build** | Docker Buildx | Container image creation |
| **Security** | Safety | Dependency vulnerability scan |
| **Integration** | cURL | API health and endpoint checks |

### Running Locally

```bash
# Clone repository
git clone https://github.com/himeshparashar/bot_gpt.git
cd bot_gpt

# Create .env file
echo "GOOGLE_API_KEY=your_key_here" > .env

# Start with Docker Compose
docker compose up --build

# Access API
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
# Health: http://localhost:8000/health
```

---

## 🧪 Testing

### Test Structure

```
tests/
├── conftest.py              # Fixtures, in-memory SQLite setup
├── test_conversation_models.py   # Model unit tests
└── test_conversation_repository.py  # Repository tests
```

### Key Test Cases

```python
class TestConversationRepository:
    def test_create_conversation(self, db_session, repo):
        """Test creating a conversation"""
        
    def test_get_conversation_by_id(self, db_session, repo, sample_conversation):
        """Test retrieving by ID"""
        
    def test_add_message(self, db_session, repo, sample_conversation):
        """Test adding messages"""
        
    def test_get_messages_ordered_by_created_at(self, db_session, repo):
        """Test message ordering"""
        
    def test_delete_conversation(self, db_session, repo, sample_conversation):
        """Test cascade delete"""
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_conversation_repository.py -v
```

---

## 📁 Project Structure

```
bot_gpt/
├── app/
│   ├── main.py                    # FastAPI application entry
│   ├── api/v1/
│   │   ├── router.py              # API router aggregation
│   │   └── endpoints/
│   │       ├── conversations.py   # Conversation CRUD endpoints
│   │       └── documents.py       # Document upload endpoints
│   ├── core/
│   │   ├── config.py              # Settings (pydantic-settings)
│   │   ├── database.py            # SQLAlchemy engine, session
│   │   └── exceptions.py          # Custom exceptions
│   ├── models/
│   │   ├── base.py                # SQLAlchemy base, mixins
│   │   ├── conversation.py        # Conversation, Message models
│   │   └── document.py            # Document model
│   ├── repositories/
│   │   ├── base.py                # Generic CRUD repository
│   │   └── conversation.py        # Conversation-specific queries
│   ├── schemas/
│   │   ├── chat.py                # Pydantic request/response schemas
│   │   └── document.py            # Document schemas
│   └── services/
│       ├── chat_service.py        # Chat orchestration
│       ├── context_manager.py     # Sliding window, token counting
│       ├── prompt_manager.py      # System prompts (Strategy Pattern)
│       ├── rag_service.py         # RAG operations
│       ├── ingestion_service.py   # Document ingestion pipeline
│       ├── document_processor/
│       │   ├── processor.py       # Text extraction
│       │   └── chunker.py         # Text chunking
│       ├── embeddings/
│       │   ├── base.py            # Abstract embedding interface
│       │   └── gemini.py          # Gemini embeddings
│       ├── llm/
│       │   ├── base.py            # Abstract LLM interface
│       │   ├── gemini.py          # Gemini provider
│       │   ├── groq.py            # Groq provider
│       │   └── openai.py          # OpenAI provider
│       └── vectorstore/
│           ├── base.py            # Abstract vector store
│           └── chroma.py          # ChromaDB implementation
├── tests/
│   ├── conftest.py                # Test fixtures
│   └── test_*.py                  # Unit tests
├── .github/workflows/ci.yml       # CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🎨 Design Patterns Used

| Pattern | Implementation | Purpose |
|---------|----------------|---------|
| **Strategy** | LLM Providers, Embeddings, Token Counters | Swappable implementations |
| **Factory** | `LLMProviderFactory`, `EmbeddingFactory` | Object creation encapsulation |
| **Repository** | `ConversationRepository`, `MessageRepository` | Data access abstraction |
| **Singleton** | `chat_service`, `prompt_manager` | Shared instances |
| **Template Method** | `BasePromptTemplate` | Prompt structure with variations |
| **Dependency Injection** | FastAPI `Depends()` | Loose coupling, testability |

---

## 🔒 Security Considerations

1. **API Keys**: Stored in environment variables, never committed
2. **CORS**: Configurable origins (currently `*` for development)
3. **Input Validation**: Pydantic schemas with constraints
4. **SQL Injection**: Prevented via SQLAlchemy ORM
5. **Dependency Scanning**: Safety checks in CI pipeline

---

## 📈 Monitoring & Observability

### Current Implementation
- **Structured Logging**: `logging` module with timestamp, level, message
- **Health Endpoint**: `/health` for liveness checks
- **OpenAPI Docs**: Auto-generated API documentation

### Future Additions
- **Prometheus Metrics**: Request latency, token usage, error rates
- **Distributed Tracing**: OpenTelemetry for request tracking
- **Centralized Logging**: ELK stack or CloudWatch

---

## 🏁 Conclusion

BOT GPT demonstrates a production-ready architecture for conversational AI backends with:

✅ **Clean Architecture**: Separation of concerns with layered design  
✅ **Flexible LLM Integration**: Multiple providers with strategy pattern  
✅ **Efficient Context Management**: Sliding window with token tracking  
✅ **RAG Support**: Document ingestion, chunking, and vector search  
✅ **Full CRUD API**: RESTful endpoints with proper HTTP semantics  
✅ **Production Ready**: Docker, CI/CD, testing, error handling  
✅ **Scalability Path**: Clear strategies for horizontal scaling  

The codebase is maintainable, extensible, and ready for production deployment with proper monitoring and scaling infrastructure.
