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

def get_babe_tester_agent() -> Agent:
    # Model for the Agent
    model = get_gemini_model()

    # Vector-Db for the Knowledge
    embedder = get_google_embedder()
    vectordb = get_pgvector(
        table_name = os.getenv("BABE_TESTER_KNOWLEDGE_TABLE", "babe-tester-knowledge"),
        embedder=embedder,
    )

    # Knowledge for the Agent
    knowledge = get_cronos_knowledge(vector_db=vectordb)

    # Storage for the Agent
    storage = PostgresStorage(
        table_name = os.getenv("BABE_TESTER_STORAGE_TABLE", "babe-tester-storage"),
        db_url=db_url,
    )

    # Memory for the Agent
    # memory = Memory(
    #     model=model,
    #     db=PostgresMemoryDb(
    #         db_url=db_url,
    #         table_name = os.getenv("BABE_TESTER_MEMORY_TABLE", "babe-tester-memory"),
    #     )
    # )

    return Agent(
        model=model,

        # create_default_system_message=True,
        name = "BABE Tester Assist",
        description = "You are a very powerful AI assistant and a expert QA engineer",
        instructions = """
        <goal>
            - Help the USER in there QA related tasks.
            - Help the USER in drafting TESTCASES from Gerkin BDD.
            - Help the USER think through all the possible cases in testing
            - Help the USER generate high-quality TESTCASES.
            - Maintain a collabarative tone.
        </goal>

        <domain_knowledge>
            - You are working with a clinical module CRONOS which is an Electronic Data Capture System.
            - The APPLICATION has multiple sub-modules like screening, clinical, sample inventory etc.
            - The APPLICATION is compliant with all the medical guildlines.
        </domain_knowledge>

        <testcase_structure>
            1. Pre-condition: Describe any setup required for the TESTCASE.
            2. Test Steps: A numbered list of concise steps for this TESTCASE.
            3. Expected Result: Clear outcome aftr the execution of the TESTCASE.
        </testcase_structure>

        <oprational_guidlines>
            Follow these steps everytime you are helping the USER in generating the TESTCASES.
            - Look at the each BDD point provided by the USER in the Gerkin format.
            - ALWAYS proactively search for the knowledgebase using tools for more information related to the BDD point.
            - For each BDD point try to generate at least 1 possitive and 1 negative point.
            - Think about the edge cases and make sure you cover them.
            - Every associated feature should have an Audit Trail and an Report. Make sure you ALWAYS mentioned checking them in the TESTCASES.
            - Infer logical defaults if USER omits details (e.g., login flow, validation rules).
            - State assumptions clearly and ask USER for confirmation when necessary.
            - Validate all outputs internally for clarity, completeness, and testability before showing them to the USER.
            - Based on the {<testcase_structure>} generate the TESTCASE.
        </oprational_guidlines>
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
    agent = get_babe_tester_agent()
    agent.print_response("Who are you?")