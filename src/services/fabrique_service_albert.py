import threading
from pathlib import Path

import requests
from fastapi import Request

from adaptateurs.adaptateur_executeur_de_requetes import AdaptateurExecuteurDeRequetes
from adaptateurs.bus_evenements import fabrique_bus_evenements
from configuration import (
    TypeReclasseur,
    recupere_configuration,
    taille_lot_reclassement,
)
from infra.albert.client_albert import fabrique_client_albert
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from question.reformulateur_de_question import ReformulateurDeQuestion
from services.reclasseur import (
    ReclasseurBGE,
    ReclasseurLLM,
    ReclasseurLLMEnParallele,
    Reclasseur,
)
from services.service_albert import ServiceAlbert, Prompts
from services.strategie_enrichissement_paragraphes import ParPagePrecedenteEtSuivante

URL_MAPPING_PAR_DEFAUT = "https://raw.githubusercontent.com/betagouv/anssi-recommandations-cyber-data/refs/heads/main/donnees/collection_reponses_maitrisees/faq_reponses_maitrisees.mapping.json"


class DepotMappingReponses:
    _mapping: MappingReponsesMaitrisees | None = None
    _lock = threading.Lock()

    @staticmethod
    def charger(url: str, session: requests.Session) -> MappingReponsesMaitrisees:
        if DepotMappingReponses._mapping is None:
            with DepotMappingReponses._lock:
                if DepotMappingReponses._mapping is None:
                    DepotMappingReponses._mapping = (
                        MappingReponsesMaitrisees.depuis_url(url, session)
                    )
        return DepotMappingReponses._mapping

    @staticmethod
    def _reinitialiser() -> None:
        with DepotMappingReponses._lock:
            DepotMappingReponses._mapping = None


def fabrique_service_albert(request: Request = None) -> ServiceAlbert:  # type: ignore[assignment]
    configuration = recupere_configuration()

    client_albert_api = fabrique_client_albert(configuration.albert.client)
    bus_evenements = fabrique_bus_evenements()
    prompt_systeme = lis_fichier_prompt("prompt_assistant_cyber.txt")
    mode_reclassement = configuration.albert.service.type_reclasseur
    prompt_reclassement = lis_fichier_prompt(
        "prompt_reclassement_llm.txt"
        if mode_reclassement is TypeReclasseur.LLM
        else "prompt_reclassement.txt"
    )
    prompt_reformulation = lis_fichier_prompt("prompt_reformulation.txt")

    reformulateur = ReformulateurDeQuestion(
        client_albert=client_albert_api,
        prompt_de_reformulation=prompt_reformulation,
        modele_reformulation=configuration.albert.client.modele_reformulation,
        bus_evenements=bus_evenements,
    )

    reclasseur: Reclasseur
    if mode_reclassement is TypeReclasseur.LLM:
        reclasseur = ReclasseurLLM(
            client_albert_api, prompt_reclassement, bus_evenements
        )
    elif mode_reclassement is TypeReclasseur.LLM_PARALLELE:
        prompt_classification = lis_fichier_prompt(
            "prompt_reclassement_llm_parallele_classification.txt"
        )
        client_reclassement = fabrique_client_albert(
            configuration.albert.client, max_retries=0
        )
        coordinateur = (
            getattr(request.app.state, "coordinateur_reclassement", None)
            if request is not None
            else None
        )
        if coordinateur is None:
            raise RuntimeError(
                "Le coordinateur de reclassement doit être ouvert dans le lifespan du serveur."
            )
        reclasseur = ReclasseurLLMEnParallele(
            client_reclassement,
            prompt_classification,
            bus_evenements,
            coordinateur=coordinateur,
            taille_lot=taille_lot_reclassement(),
        )
    else:
        reclasseur = ReclasseurBGE(
            client_albert_api,
            configuration.albert.service.modele_reclassement,
            prompt_reclassement,
            configuration.albert.service.nombre_paragraphes,
        )

    return ServiceAlbert(
        configuration_service_albert=configuration.albert.service,
        client=client_albert_api,
        utilise_recherche_hybride=configuration.albert.client.utilise_recherche_hybride,
        prompts=Prompts(
            prompt_systeme=prompt_systeme,
            prompt_reclassement=prompt_reclassement,
        ),
        reformulateur=reformulateur,
        mapping_reponses=DepotMappingReponses.charger(
            URL_MAPPING_PAR_DEFAUT,
            requests.Session(),
        ),
        reclasseur=reclasseur,
        executeur_de_requetes=AdaptateurExecuteurDeRequetes(
            timeout=(5, 10)
            if mode_reclassement is TypeReclasseur.LLM_PARALLELE
            else None
        ),
        bus_evenements=bus_evenements,
        strategie_enrichissement=ParPagePrecedenteEtSuivante(client_albert_api),
    )


def lis_fichier_prompt(nom_fichier_prompt: str) -> str:
    template_path = Path.cwd() / "templates" / nom_fichier_prompt
    return template_path.read_text(encoding="utf-8")
