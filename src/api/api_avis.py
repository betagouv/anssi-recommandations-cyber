from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from typing_extensions import Literal

from adaptateurs.journal import (
    AdaptateurJournal,
    fabrique_adaptateur_journal,
    TypeEvenement,
    AvisCompletudeSoumis,
    AvisPertinenceSoumis,
    AvisSoumis,
    DonneesAvisSoumis,
)

api_avis = APIRouter(prefix="/avis")


class AvisPertinence(BaseModel):
    valeur: Literal["très pertinente", "pertinente", "correcte", "erronée"]
    commentaire: Optional[str] = None
    informations_erronees: Optional[str] = Field(default=None, validate_default=True)

    @field_validator("informations_erronees")
    @classmethod
    def informations_erronees_obligatoire_si_exactitude_fausse(
        cls,
        commentaire: Optional[str],
        informations: ValidationInfo,
    ) -> Optional[str]:
        return valide_commentaire_avis(
            informations, commentaire, "la pertinence", "informations_erronees"
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

    if valeur == "erronée" or valeur == "fausse":
        if commentaire is None or commentaire.strip() == "":
            raise ValueError(
                f"Le champ '{champ}' est obligatoire lorsque {type_avis} est {valeur}."
            )
        if len(commentaire.strip()) < 50:
            raise ValueError(
                f"Le champ '{champ}' doit contenir au moins 50 caractères."
            )
        if len(commentaire.strip()) > 5_000:
            raise ValueError(
                f"Le champ '{champ}' ne peut contenir que 5000 caractères maximum."
            )

    return commentaire


class Avis(BaseModel):
    pertinence: AvisPertinence
    completude: AvisCompletude


class DonneesAvis(BaseModel):
    id_interaction: str
    id_conversation: str
    avis: Avis


@api_avis.post("/")
def ajoute_avis(
    requete: DonneesAvis,
    adaptateur_journal: AdaptateurJournal = Depends(fabrique_adaptateur_journal),
):
    avis_soumis = AvisSoumis(
        pertinence=AvisPertinenceSoumis(
            valeur=requete.avis.pertinence.valeur,
            commentaire=requete.avis.pertinence.commentaire,
            informations_erronees=requete.avis.pertinence.informations_erronees,
        ),
        completude=AvisCompletudeSoumis(
            valeur=requete.avis.completude.valeur,
            commentaire=requete.avis.completude.commentaire,
            informations_erronees=requete.avis.completude.informations_erronees,
            sources_adaptees=requete.avis.completude.sources_adaptees,
        ),
    )
    adaptateur_journal.consigne_evenement(
        type=TypeEvenement.AVIS_AVANCE_SOUMIS,
        donnees=DonneesAvisSoumis(
            id_interaction=requete.id_interaction,
            id_conversation=requete.id_conversation,
            avis=avis_soumis,
        ),
    )
