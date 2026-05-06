from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse, Response
from uuid import UUID

from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.journal import (
    AdaptateurJournal,
    fabrique_adaptateur_journal,
    TypeEvenement,
    DonneesDocumentSourceVisionne,
)
from infra.fast_api.fabrique_adaptateur_base_de_donnees import (
    fabrique_adaptateur_base_de_donnees,
)

document_source = APIRouter(prefix="/source")


@document_source.get("/", status_code=301)
def route_document_source(
    document: str,
    page: int,
    interaction: UUID,
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees
    ),
    adaptateur_journal: AdaptateurJournal = Depends(fabrique_adaptateur_journal),
):
    conversation_recuperee = (
        adaptateur_base_de_donnees.recupere_conversation_par_id_interaction(interaction)
    )
    if not conversation_recuperee:
        return Response(status_code=404)
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
        return Response(status_code=404)
    document_cible = documents_trouves[0]
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
