import httpx
import requests
from fastapi import Response
from pydantic import BaseModel
from typing import Any, Callable


class AdaptateurExecuteurDeRequetes:
    def __init__(
        self,
        timeout: float | tuple[float, float] | None = None,
        session_factory: Callable[[], Any] = requests.Session,
    ) -> None:
        self.timeout = timeout
        self.session_factory = session_factory

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
        with self.session_factory() as session:
            reponse = session.get(url, timeout=self.timeout)
            reponse.raise_for_status()
            contenu = reponse.json()
            if isinstance(contenu, list):
                return [base_model.model_validate(item) for item in contenu]
            return base_model.model_validate(contenu)


def fabrique_adaptateur_executeur_de_requetes() -> AdaptateurExecuteurDeRequetes:
    return AdaptateurExecuteurDeRequetes()
