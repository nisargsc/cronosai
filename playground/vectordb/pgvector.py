import os
from agno.vectordb.pgvector import PgVector, SearchType
from agno.embedder import Embedder

def get_pgvector(table_name: str, embedder: Embedder)-> PgVector:
    db_url=os.getenv("PGVECTOR_URI", "postgresql+psycopg://ai:ai@localhost:5532/ai")
    pgvector = PgVector(
        table_name=table_name, 
        db_url=db_url, 
        search_type=SearchType.hybrid,
        embedder=embedder
    )

    return pgvector
