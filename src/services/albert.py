from pathlib import Path
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice
from schemas.client_albert import (
    Paragraphe,
    ReponseQuestion,
    RecherchePayload,
)
from schemas.violations import (
    REPONSE_PAR_DEFAUT,
    Violation,
    ViolationIdentite,
    ViolationMalveillance,
    ViolationThematique,
)
from clients.albert import ClientAlbertApi, ClientAlbertHttp
from configuration import recupere_configuration, Albert
from typing import Optional, cast


class ServiceAlbert:
    def __init__(
        self,
        configuration: Albert.Service,  # type: ignore [name-defined]
        client: ClientAlbertApi,
        prompt_systeme: str,
    ) -> None:
        self.id_collection = configuration.collection_id_anssi_lab
        self.PROMPT_SYSTEME = prompt_systeme
        self.client = client

    def recherche_paragraphes(self, question: str) -> list[Paragraphe]:
        payload = RecherchePayload(
            collections=[self.id_collection],
            k=5,
            prompt=question,
            method="semantic",
        )

        donnees = self.client.recherche(payload)

        def _transforme_en_paragraphe(donnee):
            return Paragraphe(
                contenu=donnee.chunk.content,
                url=donnee.chunk.metadata.source_url,
                score_similarite=donnee.score,
                numero_page=donnee.chunk.metadata.page,
                nom_document=donnee.chunk.metadata.nom_document,
            )

        return list(map(_transforme_en_paragraphe, donnees))

    def pose_question(
        self, question: str, prompt: Optional[str] = None
    ) -> ReponseQuestion:
        paragraphes = self.recherche_paragraphes(question)
        paragraphes_concatenes = "\n\n\n".join([p.contenu for p in paragraphes])

        prompt_systeme = prompt if prompt else self.PROMPT_SYSTEME

        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": prompt_systeme.format(chunks=paragraphes_concatenes),
            },
            {
                "role": "user",
                "content": f"Question :\n{question}",
            },
        ]
        propositions_albert = self.client.recupere_propositions(messages)
        (reponse, paragraphes, violation) = (
            self._recupere_reponse_paragraphes_et_violation(
                propositions_albert, paragraphes
            )
        )

        return ReponseQuestion(
            reponse=reponse,
            paragraphes=paragraphes,
            question=question,
            violation=violation,
        )

    def _recupere_reponse_paragraphes_et_violation(
        self, propositions_albert: list[Choice], paragraphes: list[Paragraphe]
    ) -> tuple[str, list[Paragraphe], Violation | None]:
        def retourne_violation(v: Violation):
            return v.reponse, [], v

        reponse_presente = len(propositions_albert) > 0

        if reponse_presente:
            reponse_albert = cast(str, propositions_albert[0].message.content)
            if "ERREUR_IDENTITÉ" in reponse_albert:
                return retourne_violation(ViolationIdentite())
            elif "ERREUR_THÉMATIQUE" in reponse_albert:
                return retourne_violation(ViolationThematique())
            elif "ERREUR_MALVEILLANCE" in reponse_albert:
                return retourne_violation(ViolationMalveillance())
            return reponse_albert, paragraphes, None
        else:
            return REPONSE_PAR_DEFAUT, [], None


def fabrique_client_albert(configuration: Albert.Client) -> ClientAlbertApi:  # type: ignore [name-defined]
    client_openai = OpenAI(
        base_url=configuration.base_url,
        api_key=configuration.api_key,
        timeout=configuration.temps_reponse_maximum_pose_question,
    )
    client_http = ClientAlbertHttp(
        base_url=configuration.base_url,
        token=configuration.api_key,
    )

    return ClientAlbertApi(client_openai, client_http, configuration)


def fabrique_service_albert() -> ServiceAlbert:
    configuration = recupere_configuration()

    client_albert_api = fabrique_client_albert(configuration.albert.client)

    template_path = Path.cwd() / "templates" / "prompt_assistant_cyber.txt"
    prompt_systeme: str = template_path.read_text(encoding="utf-8")

    return ServiceAlbert(
        configuration=configuration.albert.service,
        client=client_albert_api,
        prompt_systeme=prompt_systeme,
    )
