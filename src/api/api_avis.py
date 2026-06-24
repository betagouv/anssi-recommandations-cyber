from typing import Optional

from typing_extensions import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field, ValidationInfo, field_validator

api_avis = APIRouter(prefix="/avis")


class AvisExactitude(BaseModel):
    valeur: Literal["très bonne", "bonne", "correcte", "fausse"]
    commentaire: Optional[str] = None
    informations_erronees: Optional[str] = Field(default=None, validate_default=True)
    sources_adaptees: Optional[str] = Field(default=None, validate_default=True)

    @field_validator("informations_erronees")
    @classmethod
    def informations_erronees_obligatoire_si_exactitude_fausse(
        cls,
        commentaire: Optional[str],
        informations: ValidationInfo,
    ) -> Optional[str]:
        return valide_commentaire_avis(
            informations, commentaire, "l'exactitude", "informations_erronees"
        )

    @field_validator("sources_adaptees")
    @classmethod
    def sources_adaptees_obligatoire_si_exactitude_fausse(
        cls,
        commentaire: Optional[str],
        informations: ValidationInfo,
    ) -> Optional[str]:
        return valide_commentaire_avis(
            informations, commentaire, "l'exactitude", "sources_adaptees"
        )


class AvisCompletude(BaseModel):
    valeur: Literal["très bonne", "bonne", "correcte", "fausse"]
    commentaire: Optional[str] = None
    informations_erronees: Optional[str] = Field(default=None, validate_default=True)

    sources_adaptees: Optional[str] = Field(default=None, validate_default=True)

    @field_validator("informations_erronees")
    @classmethod
    def informations_erronees_obligatoire_si_exactitude_fausse(
        cls,
        commentaire: Optional[str],
        informations: ValidationInfo,
    ) -> Optional[str]:
        return valide_commentaire_avis(
            informations, commentaire, "la complétude", "informations_erronees"
        )

    @field_validator("sources_adaptees")
    @classmethod
    def sources_adaptees_obligatoire_si_exactitude_fausse(
        cls,
        commentaire: Optional[str],
        informations: ValidationInfo,
    ) -> Optional[str]:
        return valide_commentaire_avis(
            informations, commentaire, "la complétude", "sources_adaptees"
        )


def valide_commentaire_avis(
    informations: ValidationInfo, commentaire: Optional[str], type_avis: str, champ: str
):
    valeur = informations.data.get("valeur")

    if valeur == "fausse" and (commentaire is None or commentaire.strip() == ""):
        raise ValueError(
            f"Le champ '{champ}' est obligatoire lorsque {type_avis} est fausse."
        )

    return commentaire


class Avis(BaseModel):
    exactitude: AvisExactitude
    completude: AvisCompletude


class DonneesAvis(BaseModel):
    id_interaction: str
    id_conversation: str
    avis: Avis


@api_avis.post("/")
def ajoute_avis(requete: DonneesAvis):
    pass
