from pathlib import Path

import pytest
from langchain_core.documents import Document
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import Chroma

from scraper import extract_pdf_links_from_html


def test_extract_pdf_links_from_html_detects_links():
    html = """
    <html>
        <body>
            <a href="/files/study1.pdf">Study 1</a>
            <iframe src="https://example.com/viewer/study2.pdf"></iframe>
            <embed src="https://cdn.example.com/assets/study3.PDF" />
        </body>
    </html>
    """
    links = extract_pdf_links_from_html(html, "https://versebyverseministry.org/base/")
    assert "https://versebyverseministry.org/files/study1.pdf" in links
    assert "https://example.com/viewer/study2.pdf" in links
    assert "https://cdn.example.com/assets/study3.PDF" in links


def test_vector_store_retrieval(tmp_path: Path):
    docs = [
        Document(
            page_content="Moses parted the Red Sea.",
            metadata={"filename": "exodus.pdf", "page_number": 1, "source_url": "http://example.com/exodus.pdf"},
        ),
        Document(
            page_content="Paul wrote letters to early churches.",
            metadata={"filename": "acts.pdf", "page_number": 3, "source_url": "http://example.com/acts.pdf"},
        ),
    ]

    embeddings = FakeEmbeddings(size=32)
    db_path = tmp_path / "chroma_db"
    vector_store = Chroma.from_documents(
        docs, embedding=embeddings, persist_directory=str(db_path)
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    results = retriever.invoke("Red Sea")
    assert results
    assert results[0].metadata["filename"] == "exodus.pdf"
