from pydantic import BaseModel
from typing import Optional


class QuestionRequete(BaseModel):
    question: str


class QuestionRequeteAvecPrompt(QuestionRequete):
    prompt: Optional[str] = None
