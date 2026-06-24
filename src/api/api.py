from fastapi import APIRouter
from typing import Dict

from api.api_avis import api_avis
from api.api_retour import api_retour
from api.conversation import api_conversation
from api.recherche import api_recherche

api = APIRouter(prefix="/api")
api.include_router(api_recherche)
api.include_router(api_conversation)
api.include_router(api_retour)
api.include_router(api_avis)
api_developpement = APIRouter(prefix="/api")


@api_developpement.get("/sante")
def route_sante() -> Dict[str, str]:
    return {"status": "ok"}
