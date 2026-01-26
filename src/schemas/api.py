from pydantic import BaseModel, Field
from typing import Optional
from schemas.albert import Paragraphe


class QuestionRequete(BaseModel):
    question: str = Field(
        max_length=5000,
        description="Votre question d'une longueur maximale de 5000 caractères.",
    )


class QuestionRequeteAvecPrompt(QuestionRequete):
    prompt: Optional[str] = None


class ReponseQuestionAPI(BaseModel):
    reponse: str
    paragraphes: list[Paragraphe]
    question: str
    interaction_id: str
