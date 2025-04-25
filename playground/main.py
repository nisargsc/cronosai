from dotenv import load_dotenv
load_dotenv()
from agno.playground import Playground, serve_playground_app

from agents.cronos import get_cronos_agent
from agents.tester import get_tester_agent
from agents.dev import get_dev_agent

cronos_agent = get_cronos_agent()
tester_agent = get_tester_agent()
dev_agent = get_dev_agent()

app = Playground(
    agents=[
        tester_agent,
        cronos_agent,
        dev_agent,
]).get_app()


if __name__ == "__main__":
    serve_playground_app("main:app",host="0.0.0.0", reload=True)
