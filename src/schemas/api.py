from pydantic import BaseModel, Field

from schemas.albert import Paragraphe


class QuestionRequete(BaseModel):
    question: str = Field(
        max_length=5000,
        description="Votre question d'une longueur maximale de 5000 caractères.",
    )
    id_conversation: str | None = None


class ReponseQuestionAPI(BaseModel):
    reponse: str
    paragraphes: list[Paragraphe]
    question: str
    id_interaction: str
    id_conversation: str
