#!/usr/bin/env python3
"""
Main entry point for the Verse by Verse RAG Chatbot
"""
import os
import sys
from src.utils.config import Config
from src.scraper.pdf_scraper import PDFScraper
from src.processor.pdf_processor import PDFProcessor
from src.rag.vector_store import VectorStoreManager
from src.rag.qa_chain import QAChain


def setup_pipeline(config: Config, force_rescrape: bool = False):
    """
    Set up the RAG pipeline
    
    Args:
        config: Configuration object
        force_rescrape: Whether to force re-scraping of PDFs
        
    Returns:
        Tuple of (vector_store_manager, qa_chain)
    """
    # Check if PDFs exist
    pdf_files = []
    if os.path.exists(config.pdf_dir) and not force_rescrape:
        pdf_files = [
            os.path.join(config.pdf_dir, f) 
            for f in os.listdir(config.pdf_dir) 
            if f.endswith('.pdf')
        ]
    
    # Scrape PDFs if needed
    if not pdf_files or force_rescrape:
        print("=" * 60)
        print("STEP 1: Scraping PDFs from Verse by Verse Ministry")
        print("=" * 60)
        scraper = PDFScraper(download_dir=config.pdf_dir)
        pdf_files = scraper.scrape_and_download(config.target_urls)
        
        if not pdf_files:
            print("Error: No PDFs were downloaded")
            sys.exit(1)
    else:
        print(f"Found {len(pdf_files)} existing PDF files")
    
    # Initialize vector store manager
    vector_store = VectorStoreManager(
        persist_directory=config.vectorstore_dir,
        embedding_model=config.embedding_model
    )
    
    # Check if vector store exists
    vectorstore_exists = os.path.exists(config.vectorstore_dir) and \
                        os.path.exists(os.path.join(config.vectorstore_dir, "chroma.sqlite3"))
    
    if vectorstore_exists and not force_rescrape:
        print("\n" + "=" * 60)
        print("Loading existing vector store...")
        print("=" * 60)
        vector_store.load_vectorstore()
    else:
        # Process PDFs
        print("\n" + "=" * 60)
        print("STEP 2: Processing PDFs and extracting text")
        print("=" * 60)
        processor = PDFProcessor(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
        documents = processor.process_multiple_pdfs(pdf_files)
        
        if not documents:
            print("Error: No documents were extracted from PDFs")
            sys.exit(1)
        
        # Create vector store
        print("\n" + "=" * 60)
        print("STEP 3: Creating vector store with embeddings")
        print("=" * 60)
        vector_store.create_vectorstore(documents)
    
    # Create QA chain
    print("\n" + "=" * 60)
    print("STEP 4: Initializing QA chain")
    print("=" * 60)
    retriever = vector_store.get_retriever(k=4)
    qa_chain = QAChain(
        retriever=retriever,
        model_name=config.chat_model
    )
    
    print("RAG pipeline ready!")
    return vector_store, qa_chain


def interactive_mode(qa_chain: QAChain):
    """
    Run the chatbot in interactive mode
    
    Args:
        qa_chain: QA chain for answering questions
    """
    print("\n" + "=" * 60)
    print("VERSE BY VERSE CHATBOT - Interactive Mode")
    print("=" * 60)
    print("Ask questions about Bible studies from Verse by Verse Ministry")
    print("Type 'quit' or 'exit' to stop")
    print("=" * 60 + "\n")
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            print("\nSearching for answer...\n")
            response = qa_chain.ask_with_sources(question)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


def main():
    """Main function"""
    # Load configuration
    config = Config()
    
    # Validate configuration
    if not config.validate():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("VERSE BY VERSE RAG CHATBOT")
    print("=" * 60)
    
    # Set up the pipeline
    force_rescrape = '--rescrape' in sys.argv
    vector_store, qa_chain = setup_pipeline(config, force_rescrape=force_rescrape)
    
    # Run interactive mode
    interactive_mode(qa_chain)


if __name__ == "__main__":
    main()
