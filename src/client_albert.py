import requests
from typing import Optional
from pathlib import Path
from openai import OpenAI
from schemas.reponses import ReponseQuestion
from config import recupere_configuration

from schemas.reponses import Paragraphe


class ClientAlbert:
    """
    Fournit une interface unique pour intéragir avec l'API web Albert.
    En particulier, on encapsule deux façons de communiquer :
    - une API HTTP "classique"
    - une API qui suit le format OpenAI
    """

    def __init__(self) -> None:
        configuration = recupere_configuration()
        self.base_url: str = configuration["BASE_URL_ALBERT"]
        self.api_key: Optional[str] = configuration["ALBERT_API_KEY"]
        self.id_collection = configuration["COLLECTION_ID_ANSSI_LAB"]
        self.modele_reponse = configuration["MODELE_REPONSE_ALBERT"]
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
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

        messages = [
            {"role": "system", "content": self.PROMPT_SYSTEM},
            {
                "role": "user",
                "content": f"Question :\n{question}\n\nDocuments :\n{paragraphes_concatenes}",
            },
        ]

        response = self.client.chat.completions.create(
            messages=messages,
            model=self.modele_reponse,
            stream=False,
        )
        return ReponseQuestion(
            reponse=response.choices[0].message.content,
            paragraphes=paragraphes,
            question=question,
        )
