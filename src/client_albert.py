import requests
from pathlib import Path
from openai import OpenAI
from schemas.client_albert import Paragraphe, ReponseQuestion
from configuration import recupere_configuration, Albert
from typing import Optional


class ClientAlbertHttp(requests.Session):
    def __init__(self, base_url: str, token: str):
        super().__init__()
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    def request(self, method: str, url: str, *args, **kwargs):
        url = f"{self.base_url}{url}"
        return super().request(method, url, *args, **kwargs)


class ClientAlbert:
    """
    Fournit une interface unique pour intéragir avec l'API web Albert.
    En particulier, on encapsule deux façons de communiquer :
    - une API HTTP "classique"
    - une API qui suit le format OpenAI
    """

    def __init__(
        self,
        configuration: Albert.Parametres,
        client_openai: OpenAI,
        client_http: requests.Session,
        prompt_systeme: str,
    ) -> None:
        self.id_collection = configuration.collection_id_anssi_lab
        self.modele_reponse = configuration.modele_reponse
        self.client = client_openai
        self.PROMPT_SYSTEM = prompt_systeme
        self.session = client_http

    def recherche_paragraphes(self, question: str) -> list[Paragraphe]:
        payload = {
            "collections": [self.id_collection],
            "k": 5,
            "prompt": question,
            "method": "semantic",
        }
        response: requests.Response = self.session.post("/search", json=payload)
        data = response.json()

        paragraphes = []
        for result in data.get("data", []):
            chunk = result.get("chunk", {})
            metadonnees = chunk.get("metadata", {})
            paragraphes.append(
                Paragraphe(
                    contenu=chunk.get("content", ""),
                    url=metadonnees.get("source_url", ""),
                    score_similarite=result.get("score", 0.0),
                    numero_page=metadonnees.get("page", 0),
                    nom_document=metadonnees.get("document_name", ""),
                )
            )

        return paragraphes

    def pose_question(
        self, question: str, prompt: Optional[str] = None
    ) -> ReponseQuestion:
        paragraphes = self.recherche_paragraphes(question)
        paragraphes_concatenes = "\n\n\n".join([p.contenu for p in paragraphes])

        prompt_systeme = prompt if prompt else self.PROMPT_SYSTEM

        messages = [
            {
                "role": "system",
                "content": prompt_systeme.format(chunks=paragraphes_concatenes),
            },
            {
                "role": "user",
                "content": f"Question :\n{question}",
            },
        ]

        reponse = self.client.chat.completions.create(
            messages=messages,
            model=self.modele_reponse,
            stream=False,
        )
        return ReponseQuestion(
            reponse=reponse.choices[0].message.content,
            paragraphes=paragraphes,
            question=question,
        )


def fabrique_client_albert() -> ClientAlbert:
    configuration = recupere_configuration()

    client_openai = OpenAI(
        base_url=configuration.albert.client.base_url,
        api_key=configuration.albert.client.api_key,
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
