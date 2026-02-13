import uuid

from typing import Callable, Optional

import pytest

from schemas.albert import ReponseQuestion
from conversation.conversation import Interaction, Conversation
from tests.conftest import ConstructeurDeReponseQuestion


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
) -> Callable[[Optional[ConstructeurDeReponseQuestion]], ConstructeurDeConversation]:
    def _un_constructeur_de_conversation(
        constructeur_de_reponse_question: Optional[
            ConstructeurDeReponseQuestion
        ] = None,
    ):
        return ConstructeurDeConversation(
            constructeur_de_reponse_question.construis()
            if constructeur_de_reponse_question is not None
            else un_constructeur_de_reponse_question().construis()
        )

    return _un_constructeur_de_conversation
