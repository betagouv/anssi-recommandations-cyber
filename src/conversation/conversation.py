import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field
from typing import NamedTuple, Optional

from adaptateurs.horloge import AdaptateurHorloge
from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import (
    RetourUtilisatrice,
)


class Interaction(BaseModel):
    reponse_question: ReponseQuestion
    retour_utilisatrice: Optional[RetourUtilisatrice] = None
    date_creation: datetime = Field(default_factory=AdaptateurHorloge.maintenant)
    id: UUID


class Conversation:
    def __init__(self, interaction: Interaction):
        self.id_conversation = uuid.uuid4()
        self._interactions = [interaction]

    @property
    def interactions(self) -> list[Interaction]:
        self._interactions.sort(key=lambda i: i.date_creation, reverse=True)
        return self._interactions

    def ajoute_interaction(self, interaction):
        self._interactions.append(interaction)

    @staticmethod
    def hydrate(id_conversation: uuid.UUID, les_interactions: list[Interaction]):
        conversation = Conversation(les_interactions[0])
        conversation.id_conversation = id_conversation
        conversation._interactions.extend(les_interactions[1:])
        return conversation


class ResultatConversation:
    def __init__(
        self,
        id_conversation: uuid.UUID,
        reponse_question: ReponseQuestion,
        interaction: Interaction,
        id_interaction: str,
    ):
        self.id_interaction = id_interaction
        self.reponse_question = reponse_question
        self.interaction = interaction
        self.id_conversation = id_conversation


class ResultatInteractionEnErreur:
    def __init__(self, e: Exception):
        self.message_mqc = "Erreur lors de l’appel à Albert"
        self.erreur = str(e)


class QuestionUtilisateur(NamedTuple):
    question: str
    conversation: uuid.UUID | None = None
