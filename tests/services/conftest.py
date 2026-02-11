import uuid

from typing import Callable

import pytest

from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import Conversation, Interaction


class ConstructeurDeConversation:
    def __init__(self, reponse_question: ReponseQuestion):
        super().__init__()
        self.interactions: list[Interaction] = []
        self.interaction = Interaction(
            reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
        )

    def avec_interaction(self, interaction: Interaction):
        self.interaction = interaction
        return self

    def ajoute_interaction(self, interaction: Interaction):
        self.interactions.append(interaction)
        return self

    def construis(self) -> Conversation:
        conversation = Conversation(self.interaction)
        for interaction in self.interactions:
            conversation.ajoute_interaction(interaction)
        return conversation


@pytest.fixture()
def un_constructeur_de_conversation(
    un_constructeur_de_reponse_question,
) -> Callable[[], ConstructeurDeConversation]:
    def _un_constructeur_de_conversation():
        return ConstructeurDeConversation(
            un_constructeur_de_reponse_question().construis()
        )

    return _un_constructeur_de_conversation


class ConstructeurDInteraction:
    def __init__(self):
        super().__init__()
        self.reponse_question = ReponseQuestion(
            reponse="Je suis Albert, pour vous servir",
            paragraphes=[],
            question="une question",
            violation=None,
        )
        self.retour_utilisatrice = None

    def construis(self) -> Interaction:
        return Interaction(
            reponse_question=self.reponse_question,
            retour_utilisatrice=self.retour_utilisatrice,
            id=uuid.uuid4(),
        )

    def avec_question(self, question: str):
        self.reponse_question = ReponseQuestion(
            reponse=f"réponse : {question}",
            paragraphes=[],
            question=question,
            violation=None,
        )
        return self


@pytest.fixture()
def un_constructeur_d_interaction() -> Callable[[], ConstructeurDInteraction]:
    def _un_constructeur_d_interaction():
        return ConstructeurDInteraction()

    return _un_constructeur_d_interaction
