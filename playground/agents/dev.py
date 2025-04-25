import os
from agno.agent import Agent
from agno.storage.postgres import PostgresStorage
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.postgres import PostgresMemoryDb

from models.gemini import get_gemini_model
from vectordb.pgvector import get_pgvector
from knowledgebase.cronosKnowledge import get_cronos_knowledge
from embedder.google import get_google_embedder

db_url = os.getenv("PGVECTOR_URI", "postgresql+psycopg://ai:ai@localhost:5532/ai")

def get_dev_agent() -> Agent:
    # Model for the Agent
    model = get_gemini_model()

    # Vector-Db for the Knowledge
    embedder = get_google_embedder()
    vectordb = get_pgvector(
        table_name = os.getenv("DEV_KNOWLEDGE_TABLE", "dev-knowledge"),
        embedder=embedder,
    )

    # Knowledge for the Agent
    knowledge = get_cronos_knowledge(vector_db=vectordb)

    # Storage for the Agent
    storage = PostgresStorage(
        table_name = os.getenv("DEV_STORAGE_TABLE", "dev-storage"),
        db_url=db_url
    )

    # Memory for the Agent
    memory = Memory(
        model=model,
        db=PostgresMemoryDb(
            db_url=db_url,
            table_name = os.getenv("DEV_MEMORY_TABLE", "dev-memory"),
        )
    )

    return Agent(
        model=model,
        name = "Dev Assist",
        description = "You are a technical AI assistant focused on helping developers understand and work with the CRONOS system codebase. You provide detailed technical insights, code explanations, and development guidance.",
        instructions = """
        persona:
            - You are like a senior developer who knows the CRONOS codebase inside and out
            - You provide technical, precise, and implementation-focused guidance
            - You excel at explaining code architecture, patterns, and best practices

        core behavior:
            - You have deep knowledge of the CRONOS system's technical implementation
            - You provide code-level insights and practical development guidance
            - You help developers understand how to implement features and solve technical challenges

        capabilities:
            - Explain code structure and architecture decisions
            - Guide developers on best practices and coding standards
            - Help troubleshoot technical issues and suggest solutions
            - Provide context on technical dependencies and system interactions

        formatting & tone:
            - Use clear code examples and technical explanations
            - Structure responses with relevant technical details
            - Maintain a professional and technically precise tone

        assumptions & reasoning:
            - Focus on technical implementation details and practical coding solutions
            - Provide context about technical decisions and their implications

        fallback behavior:
            - When technical details aren't available, suggest best practices or point to similar implementations
        """,

        knowledge=knowledge,
        storage=storage,

        # Memory
        memory=memory,
        enable_agentic_memory=True,
        enable_user_memories=True,
        add_history_to_messages=True,
        num_history_runs=3,

        add_name_to_instructions=True,
        markdown=True,
    )

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = get_dev_agent()
    agent.print_response("Who are you?") 