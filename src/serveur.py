import gradio as gr
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from typing import Dict, Any
from client_albert import ClientAlbert, fabrique_client_albert
from schemas.api import QuestionRequete, QuestionRequeteAvecPrompt, ReponseQuestion
from schemas.client_albert import Paragraphe
from gradio_app import cree_interface_gradio
from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.adaptateur_base_de_donnees_postgres import (
    fabrique_adaptateur_base_de_donnees_retour_utilisatrice,
)
from schemas.retour_utilisatrice import (
    RetourUtilisatrice,
    DonneesCreationRetourUtilisateur,
)
from configuration import Mode

api = APIRouter(prefix="/api")
api_developpement = APIRouter(prefix="/debug")


@api_developpement.get("/sante")
def route_sante() -> Dict[str, str]:
    return {"status": "ok"}


@api_developpement.post("/pose_question")
def route_pose_question_avec_prompt(
    request: QuestionRequeteAvecPrompt,
    client_albert: ClientAlbert = Depends(fabrique_client_albert),
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> ReponseQuestion:
    reponse_question = client_albert.pose_question(request.question, request.prompt)
    id_interaction = adaptateur_base_de_donnes.sauvegarde_interaction(reponse_question)
    return ReponseQuestion(
        **reponse_question.model_dump(), interaction_id=id_interaction
    )


@api.post("/recherche")
def route_recherche(
    request: QuestionRequete,
    client_albert: ClientAlbert = Depends(fabrique_client_albert),
) -> list[Paragraphe]:
    return client_albert.recherche_paragraphes(request.question)


@api.post("/pose_question")
def route_pose_question(
    request: QuestionRequete,
    client_albert: ClientAlbert = Depends(fabrique_client_albert),
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> ReponseQuestion:
    reponse_question = client_albert.pose_question(request.question)
    id_interaction = adaptateur_base_de_donnes.sauvegarde_interaction(reponse_question)
    return ReponseQuestion(
        **reponse_question.model_dump(), interaction_id=id_interaction
    )


@api.post("/retour")
def route_retour(
    body: DonneesCreationRetourUtilisateur,
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> Dict[str, Any]:
    retour = RetourUtilisatrice(
        pouce_leve=body.retour.pouce_leve, commentaire=body.retour.commentaire
    )
    succes = adaptateur_base_de_donnes.ajoute_retour_utilisatrice(
        body.id_interaction_rattachee, retour
    )

    if not succes:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")

    return {"succes": True, "commentaire": body.retour.commentaire}


def fabrique_serveur(mode: Mode) -> FastAPI:
    serveur = FastAPI()

    serveur.include_router(api)
    if mode == Mode.DEVELOPPEMENT:
        serveur.include_router(api_developpement)

    interface = cree_interface_gradio(serveur)
    serveur = gr.mount_gradio_app(serveur, interface, path="/ui")

    return serveur
