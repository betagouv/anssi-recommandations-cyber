import httpx
import requests
from fastapi import Response
from pydantic import BaseModel


class AdaptateurExecuteurDeRequetes:
    async def get_asynchrone(self, url: str) -> Response:
        try:
            async with httpx.AsyncClient() as client:
                reponse = await client.get(url, follow_redirects=True)
                reponse.raise_for_status()

                return Response(
                    content=reponse.content,
                    media_type=reponse.headers.get("content-type"),
                )
        except Exception:
            return Response(status_code=502)

    def recupere(self, url: str, base_model: type[BaseModel]):
        session = requests.Session()
        reponse = session.get(url)
        reponse.raise_for_status()
        if isinstance(reponse.json(), list):
            return [base_model.model_validate(item) for item in reponse.json()]
        return base_model.model_validate(reponse.json())


def fabrique_adaptateur_executeur_de_requetes() -> AdaptateurExecuteurDeRequetes:
    return AdaptateurExecuteurDeRequetes()
