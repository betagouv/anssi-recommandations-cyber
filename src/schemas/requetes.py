from pydantic import BaseModel
from typing import Optional


class QuestionRequete(BaseModel):
    question: str


class QuestionRequeteAvecSurcharge(QuestionRequete):
    prompt_surcharge: Optional[str] = None
