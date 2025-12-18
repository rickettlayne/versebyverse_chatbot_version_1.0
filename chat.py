from __future__ import annotations

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DIR = Path("./data/chroma_db")


def build_retriever():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is required in the environment or .env")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", openai_api_key=api_key
    )
    vector_store = Chroma(
        persist_directory=str(CHROMA_DIR), embedding_function=embeddings
    )
    return vector_store.as_retriever(search_kwargs={"k": 4})


def format_sources(documents) -> str:
    sources: List[str] = []
    for doc in documents:
        filename = doc.metadata.get("filename", "unknown")
        page = doc.metadata.get("page_number", "n/a")
        sources.append(f"{filename} (p.{page})")
    if not sources:
        return "None"
    return "; ".join(sorted(set(sources)))


def format_context(documents) -> str:
    return "\n\n".join(
        f"[{doc.metadata.get('filename','unknown')} p.{doc.metadata.get('page_number','?')}] {doc.page_content}"
        for doc in documents
    )


def build_chain():
    retriever = build_retriever()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=(
                    "You are a Bible study assistant. "
                    "Answer the user's question using only the provided context excerpts. "
                    "If the context does not contain the answer, reply with "
                    '"I cannot answer this based on the provided study materials." '
                    "Keep answers concise and factual."
                )
            ),
            ("human", "Question: {question}\n\nContext:\n{context}"),
        ]
    )

    def chain_func(question: str):
        documents = retriever.invoke(question)
        if not documents:
            return (
                "I cannot answer this based on the provided study materials.\n\nSources: None"
            )

        context = format_context(documents)
        response = (prompt | model | StrOutputParser()).invoke(
            {"question": question, "context": context}
        )
        return f"{response}\n\nSources: {format_sources(documents)}"

    return chain_func


def chat_cli():
    chat_fn = build_chain()
    print("Bible Study RAG Chatbot. Type 'exit' to quit.")
    while True:
        try:
            user_input = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue
        answer = chat_fn(user_input)
        print(answer)


if __name__ == "__main__":
    chat_cli()
