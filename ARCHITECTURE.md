# Architecture Documentation

## System Overview

The Verse by Verse RAG Chatbot is built using a modular, pipeline-based architecture that processes Bible study materials and enables intelligent question-answering.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (CLI)                     │
│                        (main.py)                             │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    RAG Pipeline Manager                      │
│                  (Orchestrates Components)                   │
└────┬──────────┬─────────────┬────────────┬──────────────────┘
     │          │              │            │
     ▼          ▼              ▼            ▼
┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────────┐
│ Scraper │ │Processor │ │ Vector  │ │  QA Chain   │
│         │ │          │ │  Store  │ │             │
└─────────┘ └──────────┘ └─────────┘ └─────────────┘
     │          │              │            │
     ▼          ▼              ▼            ▼
┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────────┐
│  PDFs   │ │Documents │ │Embeddings│ │  Answers    │
└─────────┘ └──────────┘ └─────────┘ └─────────────┘
```

## Component Details

### 1. Scraper Module (`src/scraper/`)

**Purpose**: Download Bible study PDFs from target websites

**Key Components**:
- `PDFScraper`: Main scraping class
  - Uses `requests` for HTTP requests
  - Uses `BeautifulSoup4` for HTML parsing
  - Implements polite scraping (rate limiting)
  - Handles errors gracefully

**Flow**:
1. Fetch HTML from target URLs
2. Parse HTML to find PDF links
3. Download PDFs to local storage
4. Skip already downloaded files

### 2. Processor Module (`src/processor/`)

**Purpose**: Extract and chunk text from PDFs

**Key Components**:
- `PDFProcessor`: Text extraction and chunking
  - Primary: `pdfplumber` for high-quality extraction
  - Fallback: `PyPDF2` for problematic PDFs
  - Uses `RecursiveCharacterTextSplitter` from LangChain

**Flow**:
1. Extract text from PDFs
2. Clean and normalize text
3. Split into overlapping chunks (default: 1000 chars, 200 overlap)
4. Create Document objects with metadata

### 3. RAG Module (`src/rag/`)

**Purpose**: Implement retrieval-augmented generation

**Key Components**:

#### 3a. Vector Store (`vector_store.py`)
- `VectorStoreManager`: Manages embeddings and retrieval
  - Uses `ChromaDB` for persistent storage
  - Uses `OpenAI Embeddings` (text-embedding-3-small)
  - Implements similarity search
  - Provides retriever interface

#### 3b. QA Chain (`qa_chain.py`)
- `QAChain`: Question-answering logic
  - Uses `GPT-4` (configurable model)
  - Custom prompt template for Bible study context
  - Returns answers with source attribution
  - Implements RetrievalQA pattern

**Flow**:
1. Convert documents to embeddings
2. Store embeddings in ChromaDB
3. For queries:
   - Embed the question
   - Find similar document chunks (k=4)
   - Pass context to LLM
   - Generate answer
   - Return with sources

### 4. Utils Module (`src/utils/`)

**Purpose**: Configuration and shared utilities

**Key Components**:
- `Config`: Environment and settings management
  - Loads from `.env` file
  - Validates required settings
  - Provides default values

## Data Flow

### Initial Setup Flow

```
1. User runs main.py
   │
2. Load Configuration (.env)
   │
3. Check for existing PDFs
   │
   ├─[No PDFs]──▶ Scrape PDFs from websites
   │              │
   │              ▼
   │          Save to data/pdfs/
   │
4. Check for existing vector store
   │
   ├─[No vector store]──▶ Process PDFs
   │                      │
   │                      ▼
   │                  Extract text & chunk
   │                      │
   │                      ▼
   │                  Create embeddings
   │                      │
   │                      ▼
   │                  Store in ChromaDB
   │
5. Initialize QA Chain
   │
6. Enter interactive mode
```

### Question-Answer Flow

```
1. User enters question
   │
2. Embed question using OpenAI
   │
3. Similarity search in vector store
   │
4. Retrieve top-k relevant chunks (k=4)
   │
5. Format context from chunks
   │
6. Send to GPT-4 with custom prompt
   │
7. Generate answer
   │
8. Format with sources
   │
9. Display to user
```

## Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Scraping | requests, BeautifulSoup4 | Download PDFs |
| PDF Processing | PyPDF2, pdfplumber | Extract text |
| RAG Framework | LangChain | Orchestrate RAG pipeline |
| Vector Database | ChromaDB | Store and search embeddings |
| Embeddings | OpenAI text-embedding-3-small | Convert text to vectors |
| LLM | OpenAI GPT-4 | Generate answers |
| Environment | python-dotenv | Manage configuration |

### Key Libraries

- **LangChain**: RAG orchestration, text splitting, chains
- **ChromaDB**: Persistent vector storage with HNSW indexing
- **OpenAI**: Embeddings and chat completions
- **BeautifulSoup4**: HTML parsing
- **pdfplumber**: PDF text extraction

## Design Decisions

### Why ChromaDB?
- **Persistent storage**: Data survives restarts
- **No external dependencies**: Embedded database
- **Fast retrieval**: HNSW algorithm for similarity search
- **Simple API**: Easy to use and maintain

### Why Two PDF Extractors?
- **pdfplumber**: Better quality for most PDFs
- **PyPDF2**: Fallback for problematic files
- **Resilience**: Ensures maximum text extraction

### Why Overlapping Chunks?
- **Context preservation**: Important information at boundaries
- **Better retrieval**: Questions may match partial contexts
- **Improved accuracy**: More complete answers

### Why Custom Prompt?
- **Domain-specific**: Tailored for Bible study content
- **Source awareness**: Encourages transparency
- **Accurate responses**: Prevents hallucination

## Performance Considerations

### Optimization Strategies

1. **Caching**: Vector store persists to disk
2. **Skip processed files**: Don't re-download or re-process
3. **Batch processing**: Process multiple PDFs efficiently
4. **Efficient chunking**: Balance between context and performance

### Scalability

- **PDFs**: Can handle hundreds of documents
- **Vector store**: ChromaDB scales to millions of embeddings
- **Retrieval**: Sub-second search times
- **Cost**: OpenAI API costs scale with usage

## Security Considerations

1. **Dependency scanning**: Using patched versions (langchain-community>=0.3.27)
2. **API key protection**: Stored in .env, excluded from git
3. **Input validation**: Config validation before processing
4. **Error handling**: Graceful degradation on failures

## Future Enhancements

### Possible Improvements

1. **Advanced scraping**: Handle JavaScript-rendered pages
2. **Multi-format support**: Word docs, web pages, etc.
3. **Enhanced retrieval**: Hybrid search, re-ranking
4. **User management**: Multiple users, conversation history
5. **Web interface**: Flask/FastAPI web app
6. **Streaming**: Stream LLM responses for better UX
7. **Caching**: Cache common queries
8. **Analytics**: Track usage, popular questions

## Deployment Options

### Local Deployment (Current)
```bash
python main.py
```

### Docker Deployment (Future)
```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

### Web Service Deployment (Future)
- Package as FastAPI application
- Deploy to cloud (AWS, GCP, Azure)
- Use managed vector DB (Pinecone, Weaviate)
- Implement authentication

## Monitoring & Maintenance

### Health Checks
- Vector store connectivity
- OpenAI API availability
- PDF source availability

### Logging
- Scraping activity
- Processing errors
- Query patterns
- API usage

### Maintenance Tasks
- Periodic re-scraping for new content
- Vector store optimization
- Dependency updates
- Security patches

## Conclusion

This architecture provides a solid foundation for a production-ready RAG application. The modular design allows for easy extension and maintenance, while the choice of technologies ensures reliability and performance.
