import os
from typing import Optional
from agno.models.google import Gemini
from agno.models.base import Model

def get_gemini_model(
    system_prompt: Optional[str] = None
) -> Model:
    model =  Gemini(
        id=os.getenv("GEMINI_MODEL_ID", "gemini-2.0-flash-lite"),
        temperature=float(os.getenv("GEMINI_TEMPERATURE", 0.4)),
        system_prompt=system_prompt,
    )

    return model
