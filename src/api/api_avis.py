from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from typing_extensions import Literal

from adaptateurs.journal import (
    AdaptateurJournal,
    fabrique_adaptateur_journal,
    TypeEvenement,
    AvisSourcesAdapteesSoumis,
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
    def informations_erronees_obligatoire_si_pertinence_erronee(
        cls,
        commentaire: Optional[str],
        informations: ValidationInfo,
    ) -> Optional[str]:
        return valide_commentaire_avis(
            informations, commentaire, "la pertinence", "informations_erronees"
        )


class AvisSourcesAdaptees(BaseModel):
    valeur: Literal["oui, tout à fait", "oui, partiellement", "non"]
    commentaire: Optional[str] = None
    liste: Optional[str] = Field(default=None, validate_default=True)
    raisons: Optional[list[str]] = Field(default=None, validate_default=True)

    @field_validator("liste")
    @classmethod
    def sources_adaptees_obligatoire_si_reponse_negative(
        cls,
        commentaire: Optional[str],
        informations: ValidationInfo,
    ) -> Optional[str]:
        return valide_commentaire_avis(
            informations, commentaire, "l’avis sur les sources adaptées", "liste"
        )

    @field_validator("raisons")
    @classmethod
    def raisons_obligatoire_si_sources_adaptees_negatives(
        cls,
        raisons: Optional[
            list[Literal["Sources peu pertinentes", "Sources manquantes"]]
        ],
        informations: ValidationInfo,
    ) -> Optional[list[Literal["Sources peu pertinentes", "Sources manquantes"]]]:
        valeur = informations.data.get("valeur")
        if valeur == "non":
            if raisons is None or len(raisons) == 0:
                raise ValueError(
                    "Le champ 'raisons' est obligatoire lorsque l’avis sur les sources adaptées est non."
                )

            if (
                "Sources peu pertinentes" not in raisons
                and "Sources manquantes" not in raisons
            ):
                raise ValueError(
                    "Le champ 'raisons' accepte comme valeurs 'Sources peu pertinentes', 'Sources manquantes'."
                )

        return raisons


def valide_commentaire_avis(
    informations: ValidationInfo, commentaire: Optional[str], type_avis: str, champ: str
):
    valeur = informations.data.get("valeur")

    if valeur == "erronée" or valeur == "non":
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
    sources_adaptees: AvisSourcesAdaptees


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
        sources_adaptees=AvisSourcesAdapteesSoumis(
            valeur=requete.avis.sources_adaptees.valeur,
            commentaire=requete.avis.sources_adaptees.commentaire,
            liste=requete.avis.sources_adaptees.liste,
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
