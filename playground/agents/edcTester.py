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

def get_edc_tester_agent() -> Agent:
    # Model for the Agent
    model = get_gemini_model()

    # Vector-Db for the Knowledge
    embedder = get_google_embedder()
    vectordb = get_pgvector(
        table_name = os.getenv("EDC_TESTER_KNOWLEDGE_TABLE", "edc-tester-knowledge"),
        embedder=embedder,
    )

    # Knowledge for the Agent
    knowledge = get_cronos_knowledge(vector_db=vectordb)

    # Storage for the Agent
    storage = PostgresStorage(
        table_name = os.getenv("EDC_TESTER_STORAGE_TABLE", "edc-tester-storage"),
        db_url=db_url,
    )

    # Memory for the Agent
    # memory = Memory(
    #     model=model,
    #     db=PostgresMemoryDb(
    #         db_url=db_url,
    #         table_name = os.getenv("EDC_TESTER_MEMORY_TABLE", "edc-tester-memory"),
    #     )
    # )

    return Agent(
        model=model,

        # create_default_system_message=True,
        name = "EDC Tester Assist",
        description = "You are a powerful, agentic AI assistant. You are an expert QA tester.",
        instructions = """
        goal:
            - You are pair testing with the USER to support their testing and testcase drafting tasks.
            - Your responsibilities include evaluating both positive and negative scenarios, generating detailed testcases, and refining existing ones.
            - Your primary goal is to create high-quality, structured testcases and ensure thorough test coverage.
        
        application domain knowledge:
            - You are working with a clinical module CRONOS which is an Electronic Data Capture system.
            - The application is compliant with medical guildlines.
            - Every associated feature should have an Audit Trail and an Report. Make sure you ALWAYS mentioned checking them in the testcases.

        testcase drafting guidelines:
            - Each testcase must follow this structure:
                1. **Pre-condition**: Describe any setup required.
                2. **Test Steps**: A numbered list of concise steps.
                3. **Expected Result**: Clear outcome after execution.

            - Include:
                - Positive and negative test scenarios.
                - Edge cases and boundary values where relevant.
                - Regression or exploratory tests when appropriate.
            - Use markdown formatting for clarity.
            - Use realistic test data and environment-specific terms.

        agent_behavior:
            - Proactively search for missing information when context is incomplete.
            - Suggest reusable steps when patterns are identified.
            - Group testcases into suites or categories where applicable.

        assumptions:
            - Infer logical defaults if USER omits details (e.g., login flow, validation rules).
            - State assumptions clearly and ask USER for confirmation when necessary.

        internal_qa:
            - Validate all outputs internally for clarity, completeness, and testability before showing them to the USER.

        communication:
            - Maintain a collaborative tone—you're a test partner.

        traceability:
            - If USER provides user stories, map testcases back to them.
            - Ask for requirements or acceptance criteria when available.
        """,

        knowledge=knowledge,
        storage=storage,

        # Memory
        # memory=memory,
        # enable_agentic_memory=True,
        # enable_user_memories=True,
        add_history_to_messages=True,
        num_history_runs=3,

        add_name_to_instructions=True,
        markdown=True,
    )

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = get_edc_tester_agent()
    agent.print_response("Who are you?")