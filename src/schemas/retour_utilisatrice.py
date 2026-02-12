import uuid
from datetime import datetime
from enum import StrEnum, auto
from typing import Generic, Literal, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field

from adaptateurs.horloge import AdaptateurHorloge
from schemas.albert import ReponseQuestion


class TagPositif(StrEnum):
    Conversation = auto()
    FacileAComprendre = auto()
    Complete = auto()
    BienStructuree = auto()
    SourcesUtiles = auto()


class TagNegatif(StrEnum):
    Conversation = auto()
    PasAssezDetaillee = auto()
    TropComplexe = auto()
    SourcesPeuUtiles = auto()
    InformationErronee = auto()
    HorsSujet = auto()


TypeDesTags = TypeVar("TypeDesTags")


class AbstractRetourUtilisatrice(BaseModel, Generic[TypeDesTags]):
    def __new__(cls, *args, **kwargs):
        """
        On doit empêcher cette instanciation au runtime...
        Mais on ne peut pas utiliser `abc.ABC` car cela n'empêcherait pas cette classe d'être instanciée directement (vu qu'elle n'a aucune méthode abstraite).

        > A class containing at least one method declared with this decorator that hasn’t been overridden yet cannot be instantiated.
        _c.f._ https://peps.python.org/pep-3119/
        """
        if cls is RetourUtilisatrice:
            raise TypeError(
                f"seul les enfants de '{cls.__name__}' ont vocation à être instanciés"
            )
        return object.__new__(cls)

    commentaire: Optional[str] = None
    horodatage: datetime = Field(default_factory=AdaptateurHorloge.maintenant)
    tags: list[TypeDesTags] = []


class RetourNegatif(AbstractRetourUtilisatrice[TagNegatif]):
    type: Literal["negatif"] = "negatif"


class RetourPositif(AbstractRetourUtilisatrice[TagPositif]):
    type: Literal["positif"] = "positif"


type RetourUtilisatrice = Union[RetourNegatif, RetourPositif]


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


class DonneesCreationRetourUtilisateur(BaseModel):
    id_interaction: str
    retour: RetourUtilisatrice
    id_conversation: Optional[str] = None
