from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_armor.presets import PRESETS  # type: ignore [import-untyped]
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from typing import Dict, Optional
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.adaptateur_base_de_donnees_postgres import (
    fabrique_adaptateur_base_de_donnees_retour_utilisatrice,
)
from adaptateurs.chiffrement import (
    AdaptateurChiffrement,
    fabrique_adaptateur_chiffrement,
)
from adaptateurs.journal import (
    AdaptateurJournal,
    DonneesInteractionCreee,
    DonneesViolationDetectee,
    TypeEvenement,
    fabrique_adaptateur_journal,
)
from configuration import Mode
from schemas.albert import Paragraphe
from schemas.api import (
    QuestionRequete,
    QuestionRequeteAvecPrompt,
    ReponseQuestion,
)
from schemas.retour_utilisatrice import DonneesCreationRetourUtilisateur
from schemas.retour_utilisatrice import RetourUtilisatrice
from services.fabrique_service_albert import fabrique_service_albert
from services.service_albert import ServiceAlbert

api = APIRouter(prefix="/api")
api_developpement = APIRouter(prefix="/api")


@api_developpement.get("/sante")
def route_sante() -> Dict[str, str]:
    return {"status": "ok"}


@api_developpement.post("/pose_question_avec_prompt")
def route_pose_question_avec_prompt(
    request: QuestionRequeteAvecPrompt,
    service_albert: ServiceAlbert = Depends(fabrique_service_albert),
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> ReponseQuestion:
    reponse_question = service_albert.pose_question(request.question, request.prompt)
    id_interaction = adaptateur_base_de_donnees.sauvegarde_interaction(reponse_question)
    return ReponseQuestion(
        **reponse_question.model_dump(), interaction_id=id_interaction
    )


@api_developpement.get("/prompt")
def route_prompt_systeme(
    service_albert: ServiceAlbert = Depends(fabrique_service_albert),
) -> str:
    return service_albert.prompt_systeme


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
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
    adaptateur_chiffrement: AdaptateurChiffrement = Depends(
        fabrique_adaptateur_chiffrement
    ),
    adaptateur_journal: AdaptateurJournal = Depends(fabrique_adaptateur_journal),
) -> ReponseQuestion:
    reponse_question = service_albert.pose_question(request.question)
    id_interaction = adaptateur_base_de_donnees.sauvegarde_interaction(reponse_question)

    adaptateur_journal.consigne_evenement(
        type=TypeEvenement.INTERACTION_CREEE,
        donnees=DonneesInteractionCreee(
            id_interaction=adaptateur_chiffrement.hache(id_interaction)
        ),
    )

    if reponse_question.violation is not None:
        adaptateur_journal.consigne_evenement(
            type=TypeEvenement.VIOLATION_DETECTEE,
            donnees=DonneesViolationDetectee(
                id_interaction=adaptateur_chiffrement.hache(id_interaction),
                type_violation=reponse_question.violation.__class__.__name__,
            ),
        )

    return ReponseQuestion(
        **reponse_question.model_dump(), interaction_id=id_interaction
    )


@api.post("/retour")
def ajoute_retour(
    body: DonneesCreationRetourUtilisateur,
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> RetourUtilisatrice:
    retour = adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        body.id_interaction, body.retour
    )

    if not retour:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")

    return retour


@api.delete("/retour/{id_interaction}")
def supprime_retour(
    id_interaction: str,
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> Optional[str]:
    id_interaction_retour_supprime = (
        adaptateur_base_de_donnees.supprime_retour_utilisatrice(id_interaction)
    )

    if not id_interaction_retour_supprime:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")

    return id_interaction_retour_supprime


def fabrique_serveur(
    max_requetes_par_minute: int,
    mode: Mode,
    adaptateur_chiffrement: AdaptateurChiffrement,
) -> FastAPI:
    serveur = FastAPI()

    limiteur = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{max_requetes_par_minute}/minute"],
    )
    serveur.state.limiter = limiteur
    # Les problèmes de types apparaissants ici sont connus ;
    # _c.f._ https://github.com/laurentS/slowapi/issues/188 .
    serveur.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore [arg-type]

    serveur.add_middleware(SlowAPIMiddleware)
    # Les problèmes de types apparaissants ici sont résolus côté `Starlette`, mais ne semblent pas encore avoir atteint `FastAPI` ;
    # _c.f._ https://github.com/Kludex/starlette/discussions/2451#discussioncomment-14855204 .
    serveur.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])  # type: ignore [arg-type]

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

        response = HTMLResponse(content=index)
        headers = PRESETS["strict"] | {
            "Content-Security-Policy": f"default-src 'self' https://lab-anssi-ui-kit-prod-s3-assets.cellar-c2.services.clever-cloud.com; style-src 'self' 'nonce-{nonce}'; script-src 'self' 'nonce-{nonce}'",
            "Cross-Origin-Embedder-Policy": "credentialless",
        }
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

        return response

    return serveur
