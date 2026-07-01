import httpx
from fastapi import Response


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


def fabrique_adaptateur_executeur_de_requetes() -> AdaptateurExecuteurDeRequetes:
    return AdaptateurExecuteurDeRequetes()
