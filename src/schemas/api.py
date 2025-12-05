from pydantic import BaseModel
from typing import Optional

from .client_albert import Paragraphe


class QuestionRequete(BaseModel):
    question: str


class QuestionRequeteAvecPrompt(QuestionRequete):
    prompt: Optional[str] = None


class ReponseQuestion(BaseModel):
    reponse: str
    paragraphes: list[Paragraphe]
    question: str
    interaction_id: str


class RequeteReclasse(BaseModel):
    prompt: str
    input: list[str]
    model: str
