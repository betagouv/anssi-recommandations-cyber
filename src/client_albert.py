import requests
from pathlib import Path
from openai import OpenAI
from schemas.reponses import ReponseQuestion
from configuration import recupere_configuration, Albert
from schemas.reponses import Paragraphe


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
    ) -> None:
        self.id_collection = configuration.collection_id_anssi_lab
        self.modele_reponse = configuration.modele_reponse
        self.client = client_openai
        self.charge_prompt()
        self.session = client_http

    def charge_prompt(self) -> None:
        template_path = Path.cwd() / "templates" / "prompt_assistant_cyber.txt"
        self.PROMPT_SYSTEM: str = template_path.read_text(encoding="utf-8")

    def recherche_paragraphes(self, question: str) -> str:
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

        return {"paragraphes": paragraphes}

    def pose_question(self, question: str) -> ReponseQuestion:
        resultat_recherche = self.recherche_paragraphes(question)
        paragraphes = resultat_recherche["paragraphes"]
        paragraphes_concatenes = "\n\n\n".join([p.contenu for p in paragraphes])
        prompt = self.PROMPT_SYSTEM.format(
            prompt=question, chunks=paragraphes_concatenes
        )
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.modele_reponse,
            stream=False,
        )

        return ReponseQuestion(
            reponse=response.choices[0].message.content,
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

    return ClientAlbert(
        configuration=configuration.albert.parametres,
        client_openai=client_openai,
        client_http=client_http,
    )
