# Verse by Verse RAG Chatbot 1.0

An end-to-end Retrieval-Augmented Generation (RAG) application that scrapes Bible study PDFs from Verse by Verse Ministry, processes them, and answers questions using only that content.

## Features

- **Automated PDF Scraping**: Downloads Bible study PDFs from Verse by Verse Ministry website
- **Text Extraction**: Extracts and processes text from PDF documents
- **Smart Chunking**: Splits documents into semantic chunks for optimal retrieval
- **Vector Storage**: Uses ChromaDB for efficient similarity search
- **RAG-based QA**: Answers questions using only the scraped Bible study materials
- **Source Attribution**: Provides source documents for each answer
- **Interactive CLI**: Easy-to-use command-line interface

## Architecture

The application follows a modular architecture:

```
src/
├── scraper/        # PDF scraping from website
├── processor/      # PDF text extraction and chunking
├── rag/           # Vector store and QA chain
└── utils/         # Configuration management
```

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/rickettlayne/versebyverse_chatbot_version_1.0.git
cd versebyverse_chatbot_version_1.0
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

Required environment variable:
- `OPENAI_API_KEY`: Your OpenAI API key for embeddings and chat

## Usage

### First Time Setup

Run the application to scrape PDFs, process them, and create the vector store:

```bash
python main.py
```

This will:
1. Scrape Bible study PDFs from the target URLs
2. Extract and chunk text from all PDFs
3. Create embeddings and store them in a vector database
4. Start the interactive chatbot

### Interactive Mode

Once set up, you can ask questions about the Bible studies:

```
Your question: What does the book of Genesis teach about creation?

Searching for answer...

Answer: [Answer based on the scraped materials]

Sources:
- Genesis_Study.pdf
- Creation_Overview.pdf
```

### Re-scraping Content

To force re-scraping and re-processing of PDFs:

```bash
python main.py --rescrape
```

### Exit

Type `quit`, `exit`, or `q` to exit the chatbot, or press `Ctrl+C`.

## Target Sources

The chatbot scrapes content from:
- Old Testament Books: https://versebyverseministry.org/bible-studies/category/old-testament-books
- New Testament Books: https://versebyverseministry.org/bible-studies/category/new-testament-books

## Configuration

You can customize the behavior by editing `.env`:

```env
# OpenAI API Key (required)
OPENAI_API_KEY=your_key_here

# Model settings
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4-turbo-preview

# Text processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Project Structure

```
versebyverse_chatbot_version_1.0/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── src/
│   ├── scraper/
│   │   └── pdf_scraper.py      # PDF scraping logic
│   ├── processor/
│   │   └── pdf_processor.py    # PDF text extraction
│   ├── rag/
│   │   ├── vector_store.py     # Vector store management
│   │   └── qa_chain.py         # QA chain implementation
│   └── utils/
│       └── config.py           # Configuration management
└── data/                  # Created at runtime (gitignored)
    ├── pdfs/             # Downloaded PDFs
    └── vectorstore/      # Vector database
```

## Technical Details

### Technologies Used

- **Web Scraping**: BeautifulSoup, Requests
- **PDF Processing**: PyPDF2, pdfplumber
- **RAG Framework**: LangChain
- **Vector Database**: ChromaDB
- **Embeddings & LLM**: OpenAI (text-embedding-3-small, GPT-4)

### RAG Pipeline

1. **Scraping**: Downloads PDFs from target URLs
2. **Extraction**: Extracts text from PDFs using multiple parsers
3. **Chunking**: Splits text into overlapping chunks for better context
4. **Embedding**: Creates vector embeddings for each chunk
5. **Storage**: Stores embeddings in ChromaDB for fast retrieval
6. **Retrieval**: Finds most relevant chunks for each question
7. **Generation**: Uses GPT-4 to generate answers based on retrieved context

## Troubleshooting

### No PDFs Downloaded
- Check internet connection
- Verify the target URLs are accessible
- Check for website changes that might affect scraping

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### OpenAI API Errors
- Verify your API key is correct in `.env`
- Check your OpenAI account has credits
- Ensure you have access to the specified models

### Vector Store Issues
- Delete `data/vectorstore/` and re-run to rebuild
- Use `--rescrape` flag to force complete rebuild

## License

This project is for educational and research purposes. Please respect the copyright of the source materials from Verse by Verse Ministry.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
