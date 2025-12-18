#!/usr/bin/env python3
"""
Example usage script for the Verse by Verse RAG Chatbot
This demonstrates how to use the chatbot programmatically
"""
import os
from src.utils.config import Config
from src.scraper.pdf_scraper import PDFScraper
from src.processor.pdf_processor import PDFProcessor
from src.rag.vector_store import VectorStoreManager
from src.rag.qa_chain import QAChain


def example_basic_usage():
    """Example: Basic usage of the RAG chatbot"""
    print("Example: Basic Usage")
    print("=" * 60)
    
    # Initialize configuration
    config = Config()
    if not config.validate():
        print("Please set OPENAI_API_KEY in .env file")
        return
    
    # Load existing vector store (assuming it's already created)
    vector_store = VectorStoreManager(
        persist_directory=config.vectorstore_dir,
        embedding_model=config.embedding_model
    )
    
    if not vector_store.load_vectorstore():
        print("Vector store not found. Please run main.py first to set up the chatbot.")
        return
    
    # Create QA chain
    retriever = vector_store.get_retriever(k=4)
    qa_chain = QAChain(retriever=retriever, model_name=config.chat_model)
    
    # Ask a question
    question = "What is the main theme of the book of Genesis?"
    print(f"\nQuestion: {question}")
    print("\nAnswer:")
    response = qa_chain.ask_with_sources(question)
    print(response)


def example_custom_scraping():
    """Example: Custom scraping with specific URLs"""
    print("\nExample: Custom Scraping")
    print("=" * 60)
    
    # Create scraper with custom directory
    scraper = PDFScraper(download_dir="data/custom_pdfs")
    
    # Define custom URLs to scrape
    custom_urls = [
        "https://versebyverseministry.org/bible-studies/category/old-testament-books"
    ]
    
    print(f"\nScraping {len(custom_urls)} URLs...")
    # Note: This would actually download PDFs in a real scenario
    # pdf_files = scraper.scrape_and_download(custom_urls)
    print("(Scraping skipped in example)")


def example_processing_specific_pdfs():
    """Example: Processing specific PDF files"""
    print("\nExample: Processing Specific PDFs")
    print("=" * 60)
    
    # Initialize processor
    processor = PDFProcessor(chunk_size=500, chunk_overlap=100)
    
    # Process specific PDFs (if they exist)
    pdf_dir = "data/pdfs"
    if os.path.exists(pdf_dir):
        pdf_files = [
            os.path.join(pdf_dir, f) 
            for f in os.listdir(pdf_dir)[:3]  # Just first 3 files for example
            if f.endswith('.pdf')
        ]
        
        if pdf_files:
            print(f"\nProcessing {len(pdf_files)} PDFs...")
            # documents = processor.process_multiple_pdfs(pdf_files)
            print("(Processing skipped in example)")
        else:
            print("No PDF files found in data/pdfs")
    else:
        print("PDF directory not found")


def example_similarity_search():
    """Example: Direct similarity search"""
    print("\nExample: Similarity Search")
    print("=" * 60)
    
    config = Config()
    if not config.validate():
        return
    
    # Load vector store
    vector_store = VectorStoreManager(
        persist_directory=config.vectorstore_dir,
        embedding_model=config.embedding_model
    )
    
    if not vector_store.load_vectorstore():
        print("Vector store not found. Please run main.py first.")
        return
    
    # Perform similarity search
    query = "creation account"
    print(f"\nSearching for: '{query}'")
    print("\nTop matching chunks:")
    
    results = vector_store.similarity_search(query, k=3)
    for i, doc in enumerate(results, 1):
        print(f"\n{i}. Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"   Preview: {doc.page_content[:150]}...")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("VERSE BY VERSE RAG CHATBOT - USAGE EXAMPLES")
    print("=" * 60 + "\n")
    
    # Run examples that don't require full setup
    print("\n1. Basic Usage Example (requires vector store)")
    print("   Run main.py first to set up the chatbot, then uncomment this example")
    # example_basic_usage()
    
    print("\n2. Custom Scraping Example")
    example_custom_scraping()
    
    print("\n3. Processing Specific PDFs Example")
    example_processing_specific_pdfs()
    
    print("\n4. Similarity Search Example (requires vector store)")
    print("   Run main.py first to set up the chatbot, then uncomment this example")
    # example_similarity_search()
    
    print("\n" + "=" * 60)
    print("\nTo use the examples that require a vector store:")
    print("1. Run: python main.py")
    print("2. Let it complete the setup")
    print("3. Uncomment the example function calls above")
    print("4. Run: python example_usage.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
