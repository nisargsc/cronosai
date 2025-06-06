import os
from pathlib import Path

from custom.knowledge.pdfKnowledge import PDFKnowledgeBase, PDFReader
from vectordb.pgvector import get_pgvector
from embedder.google import get_google_embedder

from agno.knowledge.agent import AgentKnowledge
from agno.vectordb.base import VectorDb
from agno.document.chunking.recursive import RecursiveChunking

def get_cronos_knowledge(
        vector_db: VectorDb,
        num_documents: int = 5
    ) -> AgentKnowledge:
    # Get the path relative to this script's location
    current_file = Path(__file__).resolve()
    # ../data/cronos/pdfs
    pdf_path = current_file.parent.parent / "data" / "babeTester" / "pdfs"
    knowledge = PDFKnowledgeBase(
        path=pdf_path,
        reader=PDFReader(),
        # Table name: ai.pdf_documents
        vector_db=vector_db,
        num_documents=num_documents,
        chunking_strategy=RecursiveChunking(),
    )

    return knowledge

# Load the knowledgebase data to vectordb
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    table_name = os.getenv("BABE_TESTER_KNOWLEDGE_TABLE", "babe-tester-knowledge")
    
    embedder = get_google_embedder()
    vectordb = get_pgvector(table_name=table_name, embedder=embedder)
    knowledge = get_cronos_knowledge(vector_db=vectordb)
    knowledge.load(upsert=True)