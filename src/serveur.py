from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Dict
from schemas.api import QuestionRequete, QuestionRequeteAvecPrompt, ReponseQuestion
from schemas.retour_utilisatrice import RetourUtilisatrice
from schemas.client_albert import Paragraphe
from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.chiffrement import (
    AdaptateurChiffrement,
    fabrique_adaptateur_chiffrement,
)
from adaptateurs.journal import (
    AdaptateurJournal,
    DonneesInteractionCreee,
    TypeEvenement,
    fabrique_adaptateur_journal,
)
from adaptateurs.adaptateur_base_de_donnees_postgres import (
    fabrique_adaptateur_base_de_donnees_retour_utilisatrice,
)
from services.albert import ServiceAlbert, fabrique_service_albert
from schemas.retour_utilisatrice import DonneesCreationRetourUtilisateur
from configuration import Mode

api = APIRouter(prefix="/api")
api_developpement = APIRouter(prefix="/api")


@api_developpement.get("/sante")
def route_sante() -> Dict[str, str]:
    return {"status": "ok"}


@api_developpement.post("/pose_question_avec_prompt")
def route_pose_question_avec_prompt(
    request: QuestionRequeteAvecPrompt,
    service_albert: ServiceAlbert = Depends(fabrique_service_albert),
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> ReponseQuestion:
    reponse_question = service_albert.pose_question(request.question, request.prompt)
    id_interaction = adaptateur_base_de_donnes.sauvegarde_interaction(reponse_question)
    return ReponseQuestion(
        **reponse_question.model_dump(), interaction_id=id_interaction
    )


@api_developpement.get("/prompt")
def route_prompt_systeme(
    service_albert: ServiceAlbert = Depends(fabrique_service_albert),
) -> str:
    return service_albert.PROMPT_SYSTEME


@api.post("/recherche")
def route_recherche(
    request: QuestionRequete,
    service_albert: ServiceAlbert = Depends(fabrique_service_albert),
) -> list[Paragraphe]:
    return service_albert.recherche_paragraphes(request.question)


@api.post("/pose_question")
def route_pose_question(
    request: QuestionRequete,
    service_albert: ServiceAlbert = Depends(fabrique_service_albert),
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
    adaptateur_chiffrement: AdaptateurChiffrement = Depends(
        fabrique_adaptateur_chiffrement
    ),
    adaptateur_journal: AdaptateurJournal = Depends(fabrique_adaptateur_journal),
) -> ReponseQuestion:
    reponse_question = service_albert.pose_question(request.question)
    id_interaction = adaptateur_base_de_donnes.sauvegarde_interaction(reponse_question)
    adaptateur_journal.consigne_evenement(
        type=TypeEvenement.INTERACTION_CREEE,
        donnees=DonneesInteractionCreee(
            id_interaction=adaptateur_chiffrement.hache(id_interaction)
        ),
    )

    return ReponseQuestion(
        **reponse_question.model_dump(), interaction_id=id_interaction
    )


@api.post("/retour")
def route_retour(
    body: DonneesCreationRetourUtilisateur,
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> RetourUtilisatrice:
    retour = adaptateur_base_de_donnes.ajoute_retour_utilisatrice(
        body.id_interaction, body.retour
    )

    if not retour:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")

    return retour


def fabrique_serveur(
    mode: Mode, adaptateur_chiffrement: AdaptateurChiffrement
) -> FastAPI:
    serveur = FastAPI()

    serveur.include_router(api)
    if mode == Mode.DEVELOPPEMENT:
        serveur.include_router(api_developpement)

    for static in ["assets", "fonts", "icons", "images"]:
        serveur.mount(f"/{static}", StaticFiles(directory=f"ui/dist/{static}"))

    @serveur.get("/")
    def index():
        nonce = adaptateur_chiffrement.recupere_nonce()
        index = (
            Path("ui/dist/index.html")
            .read_text(encoding="utf-8")
            .replace("%%NONCE_A_INJECTER%%", nonce)
        )

        return HTMLResponse(index)

    return serveur
