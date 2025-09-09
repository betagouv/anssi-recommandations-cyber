from pydantic import BaseModel


class ReponseQuestion(BaseModel):
    reponse: str
    paragraphes: str
    question: str
