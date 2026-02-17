from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional

from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.chiffrement import (
    AdaptateurChiffrement,
    fabrique_adaptateur_chiffrement,
)
from adaptateurs.journal import (
    AdaptateurJournal,
    fabrique_adaptateur_journal,
    TypeEvenement,
    DonneesAvisUtilisateurSoumis,
    DonneesAvisUtilisateurSupprime,
)
from api.conversation import extrais_type_utilisateur, api_conversation
from api.recherche import api_recherche
from infra.fast_api.fabrique_adaptateur_base_de_donnees import (
    fabrique_adaptateur_base_de_donnees,
)
from question.question import ajoute_retour_utilisatrice, supprime_retour_utilisatrice
from schemas.retour_utilisatrice import (
    DonneesCreationRetourUtilisateur,
    RetourUtilisatrice,
)

api = APIRouter(prefix="/api")
api.include_router(api_recherche)
api.include_router(api_conversation)
api_developpement = APIRouter(prefix="/api")


@api_developpement.get("/sante")
def route_sante() -> Dict[str, str]:
    return {"status": "ok"}


@api.post("/retour")
def ajoute_retour(
    body: DonneesCreationRetourUtilisateur,
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees
    ),
    adaptateur_chiffrement: AdaptateurChiffrement = Depends(
        fabrique_adaptateur_chiffrement
    ),
    adaptateur_journal: AdaptateurJournal = Depends(fabrique_adaptateur_journal),
    type_utilisateur: str | None = None,
) -> RetourUtilisatrice:
    retour = ajoute_retour_utilisatrice(body, adaptateur_base_de_donnees)

    if not retour:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")

    adaptateur_journal.consigne_evenement(
        type=TypeEvenement.AVIS_UTILISATEUR_SOUMIS,
        donnees=DonneesAvisUtilisateurSoumis(
            id_interaction=body.id_interaction,
            type_retour=body.retour.type,
            tags=list(body.retour.tags),
            type_utilisateur=extrais_type_utilisateur(
                adaptateur_chiffrement=adaptateur_chiffrement,
                type_utilisateur=type_utilisateur,
            ),
        ),
    )

    return retour


@api.delete("/retour/{id_interaction}")
def supprime_retour(
    id_interaction: str,
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees
    ),
    adaptateur_chiffrement: AdaptateurChiffrement = Depends(
        fabrique_adaptateur_chiffrement
    ),
    adaptateur_journal: AdaptateurJournal = Depends(fabrique_adaptateur_journal),
    type_utilisateur: str | None = None,
) -> Optional[str]:
    interaction = adaptateur_base_de_donnees.recupere_interaction(UUID(id_interaction))
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")

    supprime_retour_utilisatrice(UUID(id_interaction), adaptateur_base_de_donnees)

    adaptateur_journal.consigne_evenement(
        type=TypeEvenement.AVIS_UTILISATEUR_SUPPRIME,
        donnees=DonneesAvisUtilisateurSupprime(
            id_interaction=id_interaction,
            type_utilisateur=extrais_type_utilisateur(
                adaptateur_chiffrement=adaptateur_chiffrement,
                type_utilisateur=type_utilisateur,
            ),
        ),
    )

    return id_interaction
