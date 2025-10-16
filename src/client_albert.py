import requests
from pathlib import Path
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion
from openai.types.chat.chat_completion import Choice
from schemas.client_albert import (
    Paragraphe,
    ReponseQuestion,
    RecherchePayload,
    ResultatRecherche,
    RechercheChunk,
    RechercheMetadonnees,
)
from configuration import recupere_configuration, Albert
from typing import Optional, cast
from openai.types import CompletionUsage
import time
from openai import APITimeoutError, APIConnectionError


class ClientAlbertHttp(requests.Session):
    def __init__(self, base_url: str, token: str):
        super().__init__()
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def request(
        self, method: str | bytes, url: str | bytes, *args, **kwargs
    ) -> requests.Response:
        if type(url) is str:
            url = f"{self.base_url}{url}"
        elif type(url) is bytes:
            url = b"%b%b" % (self.base_url.encode("utf-8"), url)
        return super().request(method, url, *args, **kwargs)


class ClientAlbert:
    """
    Fournit une interface unique pour intéragir avec l'API web Albert.
    En particulier, on encapsule deux façons de communiquer :
    - une API HTTP "classique"
    - une API qui suit le format OpenAI
    """

    REPONSE_PAR_DEFAULT = (
        "Désolé, nous n'avons pu générer aucune réponse correspondant à votre question."
    )
    REPONSE_VIOLATION_IDENTITE = "Je suis un service développé par ou pour l’ANSSI afin de répondre aux questions en cybersécurité et informatique, en m’appuyant sur les guides officiels disponibles sur le site de l’agence."
    REPONSE_VIOLATION_THEMATIQUE = "Cette thématique n’entre pas dans le cadre de mes compétences et des sources disponibles. Reformulez votre question autour d’un enjeu cybersécurité ou informatique."
    REPONSE_VIOLATION_MALVEILLANCE = REPONSE_PAR_DEFAULT

    def __init__(
        self,
        configuration: Albert.Parametres,  # type: ignore [name-defined]
        client_openai: OpenAI,
        client_http: requests.Session,
        prompt_systeme: str,
    ) -> None:
        self.id_collection = configuration.collection_id_anssi_lab
        self.modele_reponse = configuration.modele_reponse
        self.PROMPT_SYSTEME = prompt_systeme
        self.client_openai = client_openai
        self.client_http = client_http
        self.temps_reponse_maximum_recherche_paragraphes = (
            configuration.temps_reponse_maximum_recherche_paragraphes
        )

    def recherche_paragraphes(self, question: str) -> list[Paragraphe]:
        payload = RecherchePayload(
            collections=[self.id_collection],
            k=5,
            prompt=question,
            method="semantic",
        )

        donnees = self.recherche(payload)

        def _transforme_en_paragraphe(donnee):
            return Paragraphe(
                contenu=donnee.chunk.content,
                url=donnee.chunk.metadata.source_url,
                score_similarite=donnee.score,
                numero_page=donnee.chunk.metadata.page,
                nom_document=donnee.chunk.metadata.document_name,
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
        propositions_albert = self.recupere_propositions(messages)
        (reponse, paragraphes) = self._recupere_reponse_et_paragraphes(
            propositions_albert, paragraphes
        )

        return ReponseQuestion(
            reponse=reponse,
            paragraphes=paragraphes,
            question=question,
        )

    def recupere_propositions(
        self, messages: list[ChatCompletionMessageParam]
    ) -> list[Choice]:
        try:
            propositions_albert = self.client_openai.chat.completions.create(
                messages=messages,
                model=self.modele_reponse,
                stream=False,
            ).choices
            return propositions_albert

        except (APITimeoutError, APIConnectionError):
            aucune_proposition = ChatCompletion(
                id="tmp-empty",
                created=int(time.time()),
                model=recupere_configuration().albert.parametres.modele_reponse,
                object="chat.completion",
                choices=[],
                usage=CompletionUsage(
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                ),
                system_fingerprint=None,
            ).choices
            return aucune_proposition

    def _recupere_reponse_et_paragraphes(
        self, propositions_albert: list[Choice], paragraphes: list[Paragraphe]
    ) -> tuple[str, list[Paragraphe]]:
        reponse_presente = len(propositions_albert) > 0

        if reponse_presente:
            reponse_albert = cast(str, propositions_albert[0].message.content)
            if "ERREUR_IDENTITÉ" in reponse_albert:
                return self.REPONSE_VIOLATION_IDENTITE, []
            elif "ERREUR_THÉMATIQUE" in reponse_albert:
                return self.REPONSE_VIOLATION_THEMATIQUE, []
            elif "ERREUR_MALVEILLANCE" in reponse_albert:
                return self.REPONSE_VIOLATION_MALVEILLANCE, []
            return reponse_albert, paragraphes
        else:
            return ClientAlbert.REPONSE_PAR_DEFAULT, []

    def recherche(self, payload: RecherchePayload) -> list[ResultatRecherche]:
        try:
            response: requests.Response = self.client_http.post(
                "/search",
                json=payload._asdict(),
                timeout=self.temps_reponse_maximum_recherche_paragraphes,
            )
            response.raise_for_status()
            brut = response.json()

            donnees = brut.get("data", [])
            resultats: list[ResultatRecherche] = []
            for r in donnees:
                chunk_dict = r.get("chunk", {})
                meta_dict = chunk_dict.get("metadata", {})

                metadata = RechercheMetadonnees(
                    source_url=meta_dict.get("source_url", ""),
                    page=meta_dict.get("page", 0),
                    document_name=meta_dict.get("document_name", ""),
                )
                chunk = RechercheChunk(
                    content=chunk_dict.get("content", ""),
                    metadata=metadata,
                )
                resultats.append(
                    ResultatRecherche(
                        chunk=chunk,
                        score=r.get("score", 0.0),
                    )
                )

        except requests.Timeout:
            resultats = []

        return resultats


def fabrique_client_albert() -> ClientAlbert:
    configuration = recupere_configuration()

    client_openai = OpenAI(
        base_url=configuration.albert.client.base_url,
        api_key=configuration.albert.client.api_key,
        timeout=configuration.albert.parametres.temps_reponse_maximum_pose_question,
    )

    client_http = ClientAlbertHttp(
        base_url=configuration.albert.client.base_url,
        token=configuration.albert.client.api_key,
    )

    template_path = Path.cwd() / "templates" / "prompt_assistant_cyber.txt"
    prompt_systeme: str = template_path.read_text(encoding="utf-8")

    return ClientAlbert(
        configuration=configuration.albert.parametres,
        client_openai=client_openai,
        client_http=client_http,
        prompt_systeme=prompt_systeme,
    )
