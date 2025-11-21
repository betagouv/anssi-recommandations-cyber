import requests
import time

from openai import APITimeoutError, APIConnectionError, OpenAI
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion
from openai.types.chat.chat_completion import Choice
from schemas.client_albert import (
    RecherchePayload,
    ResultatRecherche,
    RechercheChunk,
    RechercheMetadonnees,
)

from configuration import logging, Albert


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


class ClientAlbertApi:
    """
    Fournit une interface unique pour intéragir avec l'API web Albert.
    En particulier, on encapsule deux façons de communiquer :
    - une API HTTP "classique"
    - une API qui suit le format OpenAI
    """

    def __init__(
        self,
        client_openai: OpenAI,
        client_http: requests.Session,
        configuration: Albert.Client,  # type: ignore [name-defined]
    ):
        self.client_openai = client_openai
        self.client_http = client_http
        self.modele_reponse = configuration.modele_reponse
        self.temps_reponse_maximum_recherche_paragraphes = (
            configuration.temps_reponse_maximum_recherche_paragraphes
        )

    def recherche(self, payload: RecherchePayload) -> list[ResultatRecherche]:
        try:
            reponse: requests.Response = self.client_http.post(
                "/search",
                json=payload._asdict(),
                timeout=self.temps_reponse_maximum_recherche_paragraphes,
            )
            reponse.raise_for_status()
            brut = reponse.json()
            donnees = brut.get("data", [])
            resultats: list[ResultatRecherche] = []

            # Albert retourne un index 0-based utilisé par la librairie `pymupdf`.
            # Pour obtenir le numéro de page réel, il faut donc ajouter +1.
            decalage_index_Albert_et_numero_de_page_lecteur = 1
            for r in donnees:
                chunk_dict = r.get("chunk", {})
                meta_dict = chunk_dict.get("metadata", {})

                metadata = RechercheMetadonnees(
                    source_url=meta_dict.get("source_url", ""),
                    page=meta_dict.get("page", 0)
                    + decalage_index_Albert_et_numero_de_page_lecteur,
                    nom_document=meta_dict.get("document_name", ""),
                )
                chunk = RechercheChunk(
                    content=chunk_dict.get("content", ""),
                    metadata=metadata,
                )
                resultats.append(
                    ResultatRecherche(
                        chunk=chunk,
                        score=float(r.get("score", "0.0")),
                    )
                )

        except (requests.HTTPError, requests.Timeout) as erreur:
            logging.error(
                f"Route `/search` de l'API Albert retourne une erreur: {erreur}"
            )
            resultats = []

        return resultats

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
                model=self.modele_reponse,
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
