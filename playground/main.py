from dotenv import load_dotenv
load_dotenv()
from agno.playground import Playground, serve_playground_app
from fastapi.middleware.cors import CORSMiddleware
import os

from agents.babeTester import get_babe_tester_agent
from agents.edcTester import get_edc_tester_agent
# from agents.cronos import get_cronos_agent
# from agents.dev import get_dev_agent

babe_tester_agent = get_babe_tester_agent()
edc_tester_agent = get_edc_tester_agent()
# cronos_agent = get_cronos_agent()
# dev_agent = get_dev_agent()

app = Playground(
    agents=[
        babe_tester_agent,
        edc_tester_agent,
        # cronos_agent,
        # dev_agent,
]).get_app()

# Get allowed origins from environment variable or use default
UI_URL = os.environ.get("UI_URL", "http://192.168.10.176:3000")
ALLOWED_ORIGINS = [UI_URL]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Allow UI origin from environment variable
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


if __name__ == "__main__":
    serve_playground_app("main:app",host="0.0.0.0", reload=True)
