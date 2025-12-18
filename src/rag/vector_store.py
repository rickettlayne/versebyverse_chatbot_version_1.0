"""
Vector Store Manager for storing and retrieving document embeddings
"""
import os
from typing import List, Optional
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


class VectorStoreManager:
    """Manages vector store for document embeddings"""
    
    def __init__(self, 
                 persist_directory: str = "data/vectorstore",
                 embedding_model: str = "text-embedding-3-small"):
        """
        Initialize the vector store manager
        
        Args:
            persist_directory: Directory to persist the vector store
            embedding_model: OpenAI embedding model to use
        """
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.vectorstore = None
    
    def create_vectorstore(self, documents: List[Document]) -> None:
        """
        Create a vector store from documents
        
        Args:
            documents: List of Document objects to add to vector store
        """
        print(f"Creating vector store with {len(documents)} documents...")
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        print("Vector store created successfully")
    
    def load_vectorstore(self) -> bool:
        """
        Load existing vector store from disk
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print("Vector store loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return False
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to existing vector store
        
        Args:
            documents: List of Document objects to add
        """
        if self.vectorstore is None:
            print("No vector store loaded. Creating new one...")
            self.create_vectorstore(documents)
        else:
            print(f"Adding {len(documents)} documents to vector store...")
            self.vectorstore.add_documents(documents)
            print("Documents added successfully")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of documents to return
            
        Returns:
            List of most similar documents
        """
        if self.vectorstore is None:
            raise ValueError("No vector store loaded. Please load or create one first.")
        
        return self.vectorstore.similarity_search(query, k=k)
    
    def get_retriever(self, k: int = 4):
        """
        Get a retriever for the vector store
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            Retriever object
        """
        if self.vectorstore is None:
            raise ValueError("No vector store loaded. Please load or create one first.")
        
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
