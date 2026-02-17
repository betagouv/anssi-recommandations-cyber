from fastapi import APIRouter, Depends

from schemas.albert import Paragraphe
from schemas.api import QuestionRequete
from services.fabrique_service_albert import fabrique_service_albert
from services.service_albert import ServiceAlbert

api_recherche = APIRouter(prefix="/recherche")


@api_recherche.post("/")
def route_recherche(
    request: QuestionRequete,
    service_albert: ServiceAlbert = Depends(fabrique_service_albert),
) -> list[Paragraphe]:
    return service_albert.recherche_paragraphes(request.question)
