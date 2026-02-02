from configuration import logging
from pathlib import Path
from typing import Optional, Dict

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.chiffrement import (
    AdaptateurChiffrement,
    fabrique_adaptateur_chiffrement,
)
from adaptateurs.journal import (
    AdaptateurJournal,
    DonneesAvisUtilisateurSoumis,
    DonneesAvisUtilisateurSupprime,
    TypeEvenement,
    fabrique_adaptateur_journal,
)
from adaptateurs.sentry import fabrique_adaptateur_sentry
from configuration import Mode
from infra.fast_api.fabrique_adaptateur_base_de_donnees import (
    fabrique_adaptateur_base_de_donnees,
)
from infra.ui_kit.version_ui_kit import version_ui_kit
from question.question import (
    pose_question_utilisateur,
    ConfigurationQuestion,
    ResultatInteraction,
    ResultatInteractionEnErreur,
)
from schemas.albert import Paragraphe
from schemas.api import (
    QuestionRequete,
    QuestionRequeteAvecPrompt,
    ReponseQuestionAPI,
)
from schemas.retour_utilisatrice import DonneesCreationRetourUtilisateur
from schemas.retour_utilisatrice import RetourUtilisatrice
from schemas.type_utilisateur import TypeUtilisateur
from services.fabrique_service_albert import fabrique_service_albert
from services.service_albert import ServiceAlbert

api = APIRouter(prefix="/api")
api_developpement = APIRouter(prefix="/api")

HEADERS_SECURITE = {
    "cross-origin-embedder-policy": "credentialless",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
    "expect-ct": "max-age=86400, enforce",
    "origin-agent-cluster": "?1",
    "strict-transport-security": "max-age=63072000; includeSubDomains; preload",
    "x-frame-options": "DENY",
    "x-content-type-options": "nosniff",
    "x-dns-prefetch-control": "off",
}


@api_developpement.get("/sante")
def route_sante() -> Dict[str, str]:
    return {"status": "ok"}


@api_developpement.post("/pose_question_avec_prompt")
def route_pose_question_avec_prompt(
    request: QuestionRequeteAvecPrompt,
    service_albert: ServiceAlbert = Depends(fabrique_service_albert),
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees
    ),
) -> ReponseQuestionAPI:
    reponse_question = service_albert.pose_question(request.question, request.prompt)
    id_interaction = adaptateur_base_de_donnees.sauvegarde_interaction(reponse_question)
    return ReponseQuestionAPI(
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
    adaptateur_chiffrement: AdaptateurChiffrement = Depends(
        fabrique_adaptateur_chiffrement
    ),
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees
    ),
    adaptateur_journal: AdaptateurJournal = Depends(fabrique_adaptateur_journal),
    type_utilisateur: str | None = None,
) -> ReponseQuestionAPI:
    question = request.question

    configuration: ConfigurationQuestion = ConfigurationQuestion(
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
        adaptateur_chiffrement=adaptateur_chiffrement,
    )
    resultat_interaction = pose_question_utilisateur(
        configuration,
        question,
        extrais_type_utilisateur(adaptateur_chiffrement, type_utilisateur),
    )

    match resultat_interaction:
        case ResultatInteraction():
            return ReponseQuestionAPI(
                **resultat_interaction.reponse_question.model_dump(),
                interaction_id=resultat_interaction.id_interaction,
            )
        case ResultatInteractionEnErreur():
            raise HTTPException(
                status_code=422,
                detail={
                    "message": resultat_interaction.message_mqc,
                },
            )


def extrais_type_utilisateur(
    adaptateur_chiffrement: AdaptateurChiffrement, type_utilisateur: str | None
) -> TypeUtilisateur:

    logging.info(f"type_utilisateur reçu : {type_utilisateur}")
    try:
        if (
            type_utilisateur is not None
            and type_utilisateur.startswith("jOr")
            and type_utilisateur[-6] == " "
        ):
            type_utilisateur = type_utilisateur.replace(" ", "+")
        type_utilisateur = (
            TypeUtilisateur(adaptateur_chiffrement.dechiffre(type_utilisateur))
            if type_utilisateur
            else TypeUtilisateur.INCONNU
        )
        if type_utilisateur not in TypeUtilisateur:
            type_utilisateur = TypeUtilisateur.INCONNU
        return type_utilisateur
    except Exception:
        return TypeUtilisateur.INCONNU


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
    retour = adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        body.id_interaction, body.retour
    )

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
    id_interaction_retour_supprime = (
        adaptateur_base_de_donnees.supprime_retour_utilisatrice(id_interaction)
    )

    if not id_interaction_retour_supprime:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")

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

    return id_interaction_retour_supprime


def fabrique_serveur(
    max_requetes_par_minute: int,
    mode: Mode,
    static_root_directory="ui/dist/",
    la_version_ui_kit=version_ui_kit,
) -> FastAPI:
    fabrique_adaptateur_sentry()
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
        serveur.mount(
            f"/{static}", StaticFiles(directory=f"{static_root_directory}{static}")
        )

    @serveur.get("/")
    def index(
        adaptateur_chiffrement: AdaptateurChiffrement = Depends(
            fabrique_adaptateur_chiffrement
        ),
    ):
        return sert_la_page_statique(
            adaptateur_chiffrement, f"{static_root_directory}/index.html"
        )

    @serveur.get("/cgu")
    def cgu(
        adaptateur_chiffrement: AdaptateurChiffrement = Depends(
            fabrique_adaptateur_chiffrement
        ),
    ):
        return sert_la_page_statique(
            adaptateur_chiffrement, f"{static_root_directory}/cgu.html"
        )

    @serveur.get("/politique-confidentialite")
    def politique_confidentialite(
        adaptateur_chiffrement: AdaptateurChiffrement = Depends(
            fabrique_adaptateur_chiffrement
        ),
    ):
        return sert_la_page_statique(
            adaptateur_chiffrement,
            f"{static_root_directory}/politique-confidentialite.html",
        )

    def sert_la_page_statique(
        adaptateur_chiffrement: AdaptateurChiffrement, page_statique: str
    ) -> HTMLResponse:
        nonce = adaptateur_chiffrement.recupere_nonce()
        page_html = (
            Path(page_statique)
            .read_text(encoding="utf-8")
            .replace("%%NONCE_A_INJECTER%%", nonce)
            .replace("%%VERSION_UI_KIT%%", la_version_ui_kit())
            .replace("%%FAVICON%%", "/icons/favicon.ico")
        )
        response = HTMLResponse(content=page_html)
        headers = HEADERS_SECURITE | {
            "Content-Security-Policy": f"default-src 'self' https://lab-anssi-ui-kit-prod-s3-assets.cellar-c2.services.clever-cloud.com; style-src 'self' 'nonce-{nonce}' https://lab-anssi-ui-kit-prod-s3-assets.cellar-c2.services.clever-cloud.com; script-src 'self' 'nonce-{nonce}'; img-src 'self' https://lab-anssi-ui-kit-prod-s3-assets.cellar-c2.services.clever-cloud.com",
            "Cross-Origin-Embedder-Policy": "credentialless",
        }
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        return response

    return serveur
