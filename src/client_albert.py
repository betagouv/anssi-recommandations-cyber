import requests
from typing import Optional
from config import ALBERT_API_KEY, BASE_URL_ALBERT, COLLECTION_ID_ANSSI_LAB


class ClientAlbert:
    def __init__(self) -> None:
        self.base_url: str = BASE_URL_ALBERT
        self.api_key: Optional[str] = ALBERT_API_KEY

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
        return response.text
