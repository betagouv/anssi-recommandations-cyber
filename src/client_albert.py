import requests
from typing import Optional
from pathlib import Path
from openai import OpenAI
from config import (
    ALBERT_API_KEY,
    BASE_URL_ALBERT,
    COLLECTION_ID_ANSSI_LAB,
    MODELE_REPONSE_ALBERT,
)


class ClientAlbert:
    """
    Fournit une interface unique pour intéragir avec l'API web Albert.
    En particulier, on encapsule deux façons de communiquer :
    - une API HTTP "classique"
    - une API qui suit le format OpenAI
    """

    def __init__(self) -> None:
        self.base_url: str = BASE_URL_ALBERT
        self.api_key: Optional[str] = ALBERT_API_KEY
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        self.charge_prompt()

    def charge_prompt(self) -> None:
        template_path = Path.cwd() / "templates" / "prompt_assistant_cyber.txt"
        self.PROMPT_SYSTEM: str = template_path.read_text(encoding="utf-8")

    def recherche_paragraphes(self, question: str) -> str:
        session: requests.Session = requests.session()
        session.headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "collections": [COLLECTION_ID_ANSSI_LAB],
            "k": 5,
            "prompt": question,
            "method": "semantic",
        }
        response: requests.Response = session.post(
            f"{self.base_url}/search", json=payload
        )
        return "\n\n\n".join(
            [result["chunk"]["content"] for result in response.json()["data"]]
        )

    def pose_question(self, question: str) -> str:
        chunks = self.recherche_paragraphes(question)
        prompt = self.PROMPT_SYSTEM.format(prompt=question, chunks=chunks)
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODELE_REPONSE_ALBERT,
            stream=False,
        )

        return response.choices[0].message.content
