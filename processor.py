from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

import pdfplumber
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

PDF_DIR = Path("./data/pdfs")
MANIFEST_PATH = PDF_DIR / "manifest.json"
CHROMA_DIR = Path("./data/chroma_db")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_manifest() -> Dict[str, str]:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def clean_text(text: str) -> str:
    return " ".join(text.split())


def load_documents(pdf_dir: Path = PDF_DIR) -> List[Document]:
    manifest = load_manifest()
    documents: List[Document] = []

    for pdf_file in pdf_dir.glob("*.pdf"):
        source_url = manifest.get(pdf_file.name, "")
        with pdfplumber.open(pdf_file) as pdf:
            for index, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                cleaned = clean_text(text)
                if not cleaned:
                    continue
                documents.append(
                    Document(
                        page_content=cleaned,
                        metadata={
                            "source_url": source_url,
                            "filename": pdf_file.name,
                            "page_number": index,
                        },
                    )
                )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_documents(documents)


def build_vector_store(documents: List[Document]):
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is required in the environment or .env")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", openai_api_key=api_key
    )
    vector_store = Chroma.from_documents(
        documents, embedding=embeddings, persist_directory=str(CHROMA_DIR)
    )
    return vector_store


def ingest() -> None:
    documents = load_documents()
    if not documents:
        raise RuntimeError("No documents found to ingest. Run scraper first.")
    build_vector_store(documents)


if __name__ == "__main__":
    ingest()
