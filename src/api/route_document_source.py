from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse
from uuid import UUID

from adaptateurs import AdaptateurBaseDeDonnees
from infra.fast_api.fabrique_adaptateur_base_de_donnees import fabrique_adaptateur_base_de_donnees

document_source = APIRouter(prefix="/source")


@document_source.get("/", status_code=301)
def route_document_source(
        document: str,
        page: int,
        interaction: UUID,
        adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(fabrique_adaptateur_base_de_donnees),
):
    interaction_recuperee = adaptateur_base_de_donnees.recupere_interaction(interaction)
    documents_trouves = list(filter(lambda p: p.nom_document == document and p.numero_page == page,
                    interaction_recuperee.reponse_question.paragraphes))
    document_cible = documents_trouves[0]
    return RedirectResponse(f"{document_cible.url}#page={page}", 301)