from typing import Optional

from client_albert_de_test import ClientAlbertMemoire
from question.reformulateur_de_question import ReformulateurDeQuestion
from schemas.retour_utilisatrice import Conversation


class ReformulateurDeQuestionDeTest(ReformulateurDeQuestion):
    def __init__(self):
        super().__init__(ClientAlbertMemoire(), "", "")

    def reformule(
        self, question: str, conversation: Optional[Conversation] = None
    ) -> str | None:
        return question
