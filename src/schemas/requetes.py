from pydantic import BaseModel


class QuestionRequete(BaseModel):
    question: str
