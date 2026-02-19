from pathlib import Path

from configuration import recupere_configuration
from infra.albert.client_albert import fabrique_client_albert
from question.reformulateur_de_question import ReformulateurDeQuestion
from services.service_albert import ServiceAlbert, Prompts


def fabrique_service_albert() -> ServiceAlbert:
    configuration = recupere_configuration()

    client_albert_api = fabrique_client_albert(configuration.albert.client)
    prompt_systeme = lis_fichier_prompt("prompt_assistant_cyber.txt")
    prompt_reclassement = lis_fichier_prompt("prompt_reclassement.txt")
    prompt_reformulation = lis_fichier_prompt("prompt_reformulation.txt")

    reformulateur = None
    if configuration.albert.service.reformulateur_active:
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
    )


def lis_fichier_prompt(nom_fichier_prompt: str) -> str:
    template_path = Path.cwd() / "templates" / nom_fichier_prompt
    return template_path.read_text(encoding="utf-8")
