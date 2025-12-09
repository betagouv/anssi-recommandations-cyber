from pathlib import Path

from configuration import recupere_configuration
from infra.albert.client_albert import fabrique_client_albert
from services.service_albert import ServiceAlbert


def fabrique_service_albert() -> ServiceAlbert:
    configuration = recupere_configuration()

    client_albert_api = fabrique_client_albert(configuration.albert.client)

    template_path = Path.cwd() / "templates" / "prompt_assistant_cyber.txt"
    prompt_systeme: str = template_path.read_text(encoding="utf-8")

    return ServiceAlbert(
        configuration_service_albert=configuration.albert.service,
        client=client_albert_api,
        prompt_systeme=prompt_systeme,
        utilise_recherche_hybride=configuration.albert.client.utilise_recherche_hybride,
    )
