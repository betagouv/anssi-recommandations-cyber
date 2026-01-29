from pydantic import BaseModel, Field
from datetime import datetime
from typing import Generic, Literal, Optional, TypeVar, Union

from adaptateurs.horloge import AdaptateurHorloge
from schemas.albert import ReponseQuestion
from enum import StrEnum, auto


class TagPositif(StrEnum):
    FacileAComprendre = auto()
    Complete = auto()
    BienStructuree = auto()
    SourcesUtiles = auto()


class TagNegatif(StrEnum):
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


class DonneesCreationRetourUtilisateur(BaseModel):
    id_interaction: str
    retour: RetourUtilisatrice
