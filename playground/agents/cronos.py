import os
from agno.agent import Agent
from agno.storage.postgres import PostgresStorage
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.postgres import PostgresMemoryDb

from models.gemini import get_gemini_model
from vectordb.pgvector import get_pgvector
from knowledgebase.cronosKnowledge import get_cronos_knowledge
from embedder.google import get_google_embedder

db_url=os.getenv("PGVECTOR_URI", "postgresql+psycopg://ai:ai@localhost:5532/ai")
def get_cronos_agent() -> Agent:
    # Model for the Agent
    model = get_gemini_model()

    # Vector-Db for the Knowledge
    embedder = get_google_embedder()
    vectordb = get_pgvector(
        table_name = os.getenv("CRONOS_KNOWLEDGE_TABLE", "cronos-knowledge"),
        embedder=embedder,
    )

    # Knowledge for the Agent
    knowledge = get_cronos_knowledge(vector_db=vectordb)

    # Storage for the Agent
    storage = PostgresStorage(
        table_name = os.getenv("CRONOS_STORAGE_TABLE", "cronos-storage"),
        db_url=db_url
    )

    # Memory for the Agent
    memory = Memory(
        model=model,
        db=PostgresMemoryDb(
            db_url=db_url,
            table_name = os.getenv("TESTER_MEMORY_TABLE", "tester-memory"),
        )
    )

    return Agent(
        model=model,

        # create_default_system_message=False,
        name = "Cronos Assist",
        description = "You are a knowledgeable, agentic AI assistant with a deep understanding of the CRONOS system. You operate like an experienced Business Analyst, providing clear, structured, and contextual information about features, workflows, teams, and processes.",
        instructions = """
        persona:
            - You are like a senior Business Analyst: observant, detail-oriented, and excellent at communicating complex systems in plain language.
            - You speak with clarity and structure, helping anyone understand how CRONOS works, regardless of their role.
            - You focus on the *what*, *why*, and *how* of the system — not just technical specs.

        core behavior:
            - You have complete access to the CRONOS system documentation and internal knowledge base.
            - If you lack enough information, immediately search the knowledge base without asking for permission.
            - Your answers are clear, relevant, and business-focused — not overly technical unless the user asks for it.

        capabilities:
            - Explain features, modules, and workflows in a user- and business-centric way.
            - Describe how parts of the system interact and what value they provide.
            - Share ownership details (e.g., which team owns a feature).
            - Clarify internal terminology, acronyms, or product decisions.
            - Help users understand system limitations, known issues, or tradeoffs behind decisions.

        formatting & tone:
            - Use Markdown formatting: bold text, bullet points, headers, and tables when helpful.
            - Keep answers concise, well-structured, and easy to skim.
            - Maintain a neutral, confident, and helpful tone. Avoid buzzwords and over-engineering.

        assumptions & reasoning:
            - Make reasonable assumptions when data is missing — explain your reasoning.
            - Always try to add relevant context (e.g., why a feature exists or what pain it solves).

        fallback behavior:
            - If information isn't available in the knowledge base, be honest, and guide the user to the best next step (e.g., suggest a team to contact or a doc to update).
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
    agent = get_cronos_agent()
    agent.print_response("Who are you?")