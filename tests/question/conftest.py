import uuid

from typing import Callable

import pytest

from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import Conversation, Interaction


class ConstructeurDeConversation:
    def __init__(self, reponse_question: ReponseQuestion):
        super().__init__()
        self.interaction = Interaction(
            reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
        )

    def construis(self) -> Conversation:
        return Conversation(self.interaction)


@pytest.fixture()
def un_constructeur_de_conversation(
    un_constructeur_de_reponse_question,
) -> Callable[[], ConstructeurDeConversation]:
    def _un_constructeur_de_conversation():
        return ConstructeurDeConversation(
            un_constructeur_de_reponse_question().construis()
        )

    return _un_constructeur_de_conversation
