# Architecture Documentation

## System Overview

AI Content Analyzer Pro is built using a modular, layered architecture that separates concerns and enables easy maintenance and scaling.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  HTML5   │  │   CSS3   │  │JavaScript│  │  Jinja2  │   │
│  │Templates │  │ Styling  │  │  Logic   │  │Templating│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Flask Application (app.py)              │   │
│  │  • Routing          • Authentication                 │   │
│  │  • Session Mgmt     • Request Handling               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Content  │  │   RAG    │  │  Export  │  │  Batch   │   │
│  │Analyzer  │  │  Chat    │  │ Service  │  │Processor │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Document Processing Layer                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   PDF    │  │   DOCX   │  │   PPTX   │  │   XLSX   │   │
│  │  Reader  │  │  Reader  │  │  Reader  │  │  Reader  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Image   │  │ YouTube  │  │   Web    │                  │
│  │  Reader  │  │  Reader  │  │ Scraper  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         AI/ML Layer                          │
│  ┌──────────────────┐  ┌─────────────────────────────┐     │
│  │  OpenAI GPT-4    │  │   Google Gemini            │     │
│  │  • Summarization │  │   • Alternative AI Model   │     │
│  │  • Q&A           │  │   • Fallback Option        │     │
│  └──────────────────┘  └─────────────────────────────┘     │
│  ┌──────────────────┐  ┌─────────────────────────────┐     │
│  │ Sentence Trans.  │  │      ChromaDB              │     │
│  │  • Embeddings    │  │   • Vector Storage         │     │
│  │  • Similarity    │  │   • Semantic Search        │     │
│  └──────────────────┘  └─────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         Data Layer                           │
│  ┌──────────────────┐  ┌─────────────────────────────┐     │
│  │  SQLite/SQLAlch  │  │      File System           │     │
│  │  • Users         │  │   • Uploads Directory      │     │
│  │  • Analyses      │  │   • Temp Files             │     │
│  │  • Collections   │  │   • Logs                   │     │
│  └──────────────────┘  └─────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

**Technologies**: HTML5, CSS3, JavaScript, Jinja2

**Components**:
- **Templates**: Server-side rendered HTML templates
- **Static Assets**: CSS files for styling, JavaScript for interactivity
- **Responsive Design**: Mobile-first approach

**Key Features**:
- Dark mode support
- Real-time feedback
- File upload with drag-and-drop
- Progressive form enhancement

### 2. Application Layer

**Technology**: Flask 3.0+

**Core Responsibilities**:
- HTTP request routing
- Session management
- User authentication (Flask-Login)
- Request validation
- Response formatting

**Key Routes**:
```python
/                    # Home page
/login              # User authentication
/register           # User registration
/analyze            # Document analysis
/chat               # RAG chat interface
/history            # Analysis history
/collections        # Collection management
/export/<format>    # Export functionality
```

### 3. Business Logic Layer

**services/analyzer.py**:
- Coordinates document analysis
- Handles different document types
- Manages analysis workflow

**chat_service.py**:
- Implements RAG system
- Manages conversation context
- Queries vector database

**export_service.py**:
- Generates PDF exports
- Creates DOCX files
- Formats Markdown
- Structures JSON output

**batch_processor.py**:
- Concurrent document processing
- Progress tracking
- Error handling for batch operations

### 4. Document Processing Layer

Each reader is specialized for its format:

**pdf_reader.py**:
- Extracts text from PDFs
- Handles multi-page documents
- Preserves structure

**docx_reader.py**:
- Parses Word documents
- Extracts formatted text
- Handles tables

**pptx_reader.py**:
- Extracts slide content
- Preserves hierarchies
- Handles notes

**xlsx_reader.py**:
- Reads spreadsheet data
- Handles multiple sheets
- Preserves structure

**image_reader.py**:
- OCR with Tesseract
- Image preprocessing
- Text extraction

**scraper.py**:
- Web content extraction
- HTML parsing
- Content cleaning

### 5. AI/ML Layer

**LLM Integration**:
- **Primary**: OpenAI GPT-4
- **Fallback**: Google Gemini
- **Use Cases**: Summarization, Q&A, content analysis

**Summarization Pipeline**:
```python
Text Input → Preprocessing → Chunking → LLM → Post-processing → Output
```

**RAG System**:
```python
Query → Embedding → Vector Search → Context Retrieval → LLM Response
```

**Vector Database (ChromaDB)**:
- Stores document embeddings
- Enables semantic search
- Supports similarity matching

### 6. Data Layer

**Database Schema**:

```sql
Users
- id (PK)
- name
- email (unique)
- password_hash
- created_at

Analyses
- id (PK)
- user_id (FK)
- collection_id (FK, nullable)
- source_type
- source_url
- content
- summary
- mode
- summary_length
- summary_format
- notes
- created_at

Collections
- id (PK)
- user_id (FK)
- name
- description
- created_at
```

## Data Flow

### Document Analysis Flow

```
1. User uploads document or provides URL
   ↓
2. Backend validates input
   ↓
3. Appropriate reader extracts content
   ↓
4. Content is preprocessed and cleaned
   ↓
5. LLM generates summary
   ↓
6. Result is saved to database
   ↓
7. Vector embedding stored in ChromaDB
   ↓
8. Response sent to user
```

### RAG Chat Flow

```
1. User asks question
   ↓
2. Question converted to embedding
   ↓
3. Vector search finds relevant documents
   ↓
4. Context assembled from search results
   ↓
5. LLM generates answer with context
   ↓
6. Response sent to user
```

## Security Architecture

**Authentication**:
- Password hashing with BCrypt
- Session-based authentication
- Flask-Login integration

**Input Validation**:
- File type checking
- Size limits
- URL validation
- SQL injection prevention (ORM)

**Data Protection**:
- Environment variables for secrets
- Secure file uploads
- XSS prevention in templates

## Scalability Considerations

**Current Architecture** (Development):
- Single server
- SQLite database
- Local file storage
- In-memory sessions

**Production Recommendations**:
- PostgreSQL for database
- Redis for sessions/caching
- Object storage (S3) for files
- Load balancer for multiple instances
- Celery for async tasks
- Docker containerization

## Performance Optimizations

1. **Database Indexing**:
   - User email (unique index)
   - Analysis timestamps
   - Collection relationships

2. **Caching**:
   - Vector embeddings cached in ChromaDB
   - Session data cached in memory

3. **Lazy Loading**:
   - Large documents chunked
   - Paginated history views

4. **Async Processing**:
   - Batch operations non-blocking
   - Background summarization

## Error Handling

**Layered Error Handling**:
1. Input validation at route level
2. Try-catch in business logic
3. Graceful degradation (fallback AI models)
4. User-friendly error messages
5. Detailed logging for debugging

## Monitoring & Logging

**Logging Levels**:
- DEBUG: Development details
- INFO: Normal operations
- WARNING: Unusual but handled situations
- ERROR: Application errors
- CRITICAL: System failures

**Key Metrics** (Recommended):
- Request latency
- Error rates
- Document processing time
- AI API response time
- Database query performance

## API Integration

**External APIs**:
- OpenAI API (GPT-4)
- Google Generative AI (Gemini)

**Rate Limiting**:
- Implemented at application level
- Respects API provider limits
- Fallback mechanisms in place

## Future Architecture Improvements

1. **Microservices**:
   - Separate services for document processing
   - Dedicated RAG service
   - Independent scaling

2. **Message Queue**:
   - RabbitMQ or Kafka for async tasks
   - Better handling of long-running operations

3. **API Gateway**:
   - REST API endpoints
   - API versioning
   - Rate limiting

4. **Containerization**:
   - Docker for all services
   - Kubernetes for orchestration

5. **CI/CD**:
   - Automated testing
   - Continuous deployment
   - Blue-green deployments
