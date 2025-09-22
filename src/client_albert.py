import requests
from typing import Optional
from pathlib import Path
from openai import OpenAI
from schemas.reponses import ReponseQuestion
from config import recupere_configuration, Configuration

from schemas.reponses import Paragraphe


class ClientAlbert:
    """
    Fournit une interface unique pour intéragir avec l'API web Albert.
    En particulier, on encapsule deux façons de communiquer :
    - une API HTTP "classique"
    - une API qui suit le format OpenAI
    """

    def __init__(self, configuration: Configuration, client_openai: OpenAI) -> None:
        self.base_url: str = configuration.BASE_URL_ALBERT
        self.api_key: Optional[str] = configuration.ALBERT_API_KEY
        self.id_collection = configuration.COLLECTION_ID_ANSSI_LAB
        self.modele_reponse = configuration.MODELE_REPONSE_ALBERT
        self.client = client_openai
        self.charge_prompt()

    def charge_prompt(self) -> None:
        template_path = Path.cwd() / "templates" / "prompt_assistant_cyber.txt"
        self.PROMPT_SYSTEM: str = template_path.read_text(encoding="utf-8")

    def recherche_paragraphes(self, question: str) -> str:
        session: requests.Session = requests.session()
        session.headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "collections": [self.id_collection],
            "k": 5,
            "prompt": question,
            "method": "semantic",
        }
        response: requests.Response = session.post(
            f"{self.base_url}/search", json=payload
        )
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
        base_url=configuration.BASE_URL_ALBERT, api_key=configuration.ALBERT_API_KEY
    )
    return ClientAlbert(configuration=configuration, client_openai=client_openai)
