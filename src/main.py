from fastapi import FastAPI, Depends
from typing import Dict
from client_albert import ClientAlbert
from schemas.requetes import QuestionRequete

app: FastAPI = FastAPI()


def fabrique_client_albert() -> ClientAlbert:
    return ClientAlbert()


@app.get("/sante")
def route_sante() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/recherche")
def route_recherche(
    request: QuestionRequete,
    client_albert: ClientAlbert = Depends(fabrique_client_albert),
) -> str:
    return client_albert.recherche_paragraphes(request.question)
