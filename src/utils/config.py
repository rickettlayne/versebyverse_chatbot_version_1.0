"""
Configuration management for the RAG chatbot
"""
import os
from dotenv import load_dotenv


class Config:
    """Configuration settings for the RAG chatbot"""
    
    def __init__(self):
        """Load configuration from environment variables"""
        load_dotenv()
        
        # OpenAI settings
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.chat_model = os.getenv("CHAT_MODEL", "gpt-4-turbo-preview")
        
        # Document processing settings
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        # Directory settings
        self.pdf_dir = "data/pdfs"
        self.vectorstore_dir = "data/vectorstore"
        
        # Target URLs
        self.target_urls = [
            "https://versebyverseministry.org/bible-studies/category/old-testament-books?category=old-testament-books",
            "https://versebyverseministry.org/bible-studies/category/new-testament-books?category=new-testament-books"
        ]
    
    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.openai_api_key:
            print("Error: OPENAI_API_KEY not set in environment variables")
            print("Please create a .env file with your OpenAI API key")
            return False
        
        return True
