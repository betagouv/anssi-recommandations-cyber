from pydantic import BaseModel


class ReponseQuestion(BaseModel):
    reponse: str
    paragraphs: str
    question: str
