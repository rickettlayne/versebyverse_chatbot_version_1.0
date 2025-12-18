"""
Question-Answering Chain for RAG
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


class QAChain:
    """Question-Answering chain using RAG"""
    
    def __init__(self, 
                 retriever,
                 model_name: str = "gpt-4-turbo-preview",
                 temperature: float = 0.0):
        """
        Initialize the QA chain
        
        Args:
            retriever: Document retriever from vector store
            model_name: OpenAI model to use
            temperature: Temperature for generation
        """
        self.retriever = retriever
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        
        # Create custom prompt template
        template = """You are a helpful Bible study assistant. Use the following pieces of context from Bible study materials to answer the question. 
If you don't know the answer based on the provided context, just say that you don't have enough information in the materials to answer that question. 
Don't try to make up an answer.

Context:
{context}

Question: {question}

Answer: """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt}
        )
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a question and get an answer
        
        Args:
            question: Question to ask
            
        Returns:
            Dictionary with 'answer' and 'source_documents'
        """
        result = self.qa_chain.invoke({"query": question})
        
        return {
            "answer": result["result"],
            "source_documents": result["source_documents"]
        }
    
    def ask_with_sources(self, question: str) -> str:
        """
        Ask a question and get formatted answer with sources
        
        Args:
            question: Question to ask
            
        Returns:
            Formatted answer with sources
        """
        result = self.ask(question)
        
        # Format the response
        response = f"Answer: {result['answer']}\n\n"
        
        if result['source_documents']:
            response += "Sources:\n"
            seen_sources = set()
            for doc in result['source_documents']:
                source = doc.metadata.get('source', 'Unknown')
                if source not in seen_sources:
                    response += f"- {source}\n"
                    seen_sources.add(source)
        
        return response
