from fastapi import APIRouter, Depends, Response
from starlette.responses import RedirectResponse
from uuid import UUID

from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.adaptateur_executeur_de_requetes import (
    AdaptateurExecuteurDeRequetes,
    fabrique_adaptateur_executeur_de_requetes,
)
from adaptateurs.journal import (
    AdaptateurJournal,
    fabrique_adaptateur_journal,
    TypeEvenement,
    DonneesDocumentSourceVisionne,
)
from infra.fast_api.fabrique_adaptateur_base_de_donnees import (
    fabrique_adaptateur_base_de_donnees,
)
from schemas.albert import Paragraphe
from schemas.retour_utilisatrice import Conversation

document_source = APIRouter(prefix="/source")


def _recupere_les_documents(adaptateur_base_de_donnees: AdaptateurBaseDeDonnees, interaction: UUID, document: str, page: int) -> tuple[Conversation, Paragraphe] | None:
    conversation_recuperee = (
        adaptateur_base_de_donnees.recupere_conversation_par_id_interaction(interaction)
    )
    if not conversation_recuperee:
        return None
    interaction_trouvee = list(
        filter(lambda i: i.id == interaction, conversation_recuperee.interactions)
    )[-1]
    documents_trouves = list(
        filter(
            lambda p: p.nom_document == document and p.numero_page == page,
            interaction_trouvee.reponse_question.paragraphes,
        )
    )
    if len(documents_trouves) == 0:
        return None
    return conversation_recuperee, documents_trouves[0]

@document_source.get("/", status_code=301)
async def route_document_source(
    document: str,
    page: int,
    interaction: UUID,
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees
    ),
    adaptateur_journal: AdaptateurJournal = Depends(fabrique_adaptateur_journal),
):
    resultat = _recupere_les_documents(adaptateur_base_de_donnees, interaction, document, page)
    if resultat is None:
        return Response(status_code=404)
    conversation_recuperee, document_cible = resultat
    adaptateur_journal.consigne_evenement(
        TypeEvenement.DOCUMENT_SOURCE_VISIONNE,
        donnees=DonneesDocumentSourceVisionne(
            nom_document=document_cible.nom_document,
            numero_page=document_cible.numero_page,
            url_document=document_cible.url,
            id_interaction=interaction,
            id_conversation=conversation_recuperee.id_conversation,
        ),
    )
    return RedirectResponse(f"{document_cible.url}#page={page}", 301)


@document_source.get("/proxy")
async def route_proxy_document(
    document: str,
    page: int,
    interaction: UUID,
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees
    ),
    adaptateur_executeur_de_requetes: AdaptateurExecuteurDeRequetes = Depends(
        fabrique_adaptateur_executeur_de_requetes
    ),
):
    resultat = _recupere_les_documents(adaptateur_base_de_donnees, interaction, document, page)
    if resultat is None:
        return Response(status_code=404)
    _, document_cible = resultat
    return await adaptateur_executeur_de_requetes.get_asynchrone(document_cible.url)
