"""
PDF Processor for extracting and chunking text from PDFs
"""
import os
from typing import List, Dict
import PyPDF2
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class PDFProcessor:
    """Process PDF files and extract text chunks for RAG"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the PDF processor
        
        Args:
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        text = ""
        
        try:
            # Try using pdfplumber first (better text extraction)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            print(f"pdfplumber failed for {pdf_path}, trying PyPDF2: {str(e)}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            except Exception as e2:
                print(f"PyPDF2 also failed for {pdf_path}: {str(e2)}")
                
        return text.strip()
    
    def process_pdf(self, pdf_path: str) -> List[Document]:
        """
        Process a PDF file and return document chunks
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of Document objects with text chunks
        """
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            print(f"Warning: No text extracted from {pdf_path}")
            return []
        
        # Create metadata
        filename = os.path.basename(pdf_path)
        metadata = {
            "source": filename,
            "file_path": pdf_path
        }
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create Document objects
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy()
            doc_metadata["chunk"] = i
            documents.append(Document(page_content=chunk, metadata=doc_metadata))
        
        return documents
    
    def process_multiple_pdfs(self, pdf_paths: List[str]) -> List[Document]:
        """
        Process multiple PDF files
        
        Args:
            pdf_paths: List of paths to PDF files
            
        Returns:
            List of Document objects from all PDFs
        """
        all_documents = []
        
        print(f"Processing {len(pdf_paths)} PDF files...")
        for pdf_path in pdf_paths:
            print(f"Processing: {os.path.basename(pdf_path)}")
            documents = self.process_pdf(pdf_path)
            all_documents.extend(documents)
            print(f"  Extracted {len(documents)} chunks")
        
        print(f"\nTotal chunks: {len(all_documents)}")
        return all_documents
