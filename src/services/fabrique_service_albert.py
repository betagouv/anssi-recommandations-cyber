import threading
from pathlib import Path

import requests

from configuration import recupere_configuration
from infra.albert.client_albert import fabrique_client_albert
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from question.reformulateur_de_question import ReformulateurDeQuestion
from services.service_albert import ServiceAlbert, Prompts

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


def fabrique_service_albert() -> ServiceAlbert:
    configuration = recupere_configuration()

    client_albert_api = fabrique_client_albert(configuration.albert.client)
    prompt_systeme = lis_fichier_prompt("prompt_assistant_cyber.txt")
    prompt_reclassement = lis_fichier_prompt("prompt_reclassement.txt")
    prompt_reformulation = lis_fichier_prompt("prompt_reformulation.txt")

    reformulateur = ReformulateurDeQuestion(
        client_albert=client_albert_api,
        prompt_de_reformulation=prompt_reformulation,
        modele_reformulation=configuration.albert.client.modele_reformulation,
    )

    return ServiceAlbert(
        configuration_service_albert=configuration.albert.service,
        client=client_albert_api,
        utilise_recherche_hybride=configuration.albert.client.utilise_recherche_hybride,
        prompts=Prompts(
            prompt_systeme=prompt_systeme, prompt_reclassement=prompt_reclassement
        ),
        reformulateur=reformulateur,
        mapping_reponses=DepotMappingReponses.charger(
            URL_MAPPING_PAR_DEFAUT,
            requests.Session(),
        ),
    )


def lis_fichier_prompt(nom_fichier_prompt: str) -> str:
    template_path = Path.cwd() / "templates" / nom_fichier_prompt
    return template_path.read_text(encoding="utf-8")
