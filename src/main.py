import uvicorn
from fastapi import FastAPI, Depends
from typing import Dict
from client_albert import ClientAlbert
from schemas.requetes import QuestionRequete
from config import HOST, PORT
from schemas.reponses import ReponseQuestion
from ui_integration import (
    route_proxy_streamlit_http,
    route_proxy_streamlit_ws,
    lifespan,
)


app: FastAPI = FastAPI(lifespan=lifespan)


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


@app.post("/pose_question")
def route_pose_question(
    request: QuestionRequete,
    client_albert: ClientAlbert = Depends(fabrique_client_albert),
) -> ReponseQuestion:
    return client_albert.pose_question(request.question)


app.api_route(
    "/ui/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
)(route_proxy_streamlit_http)

app.websocket("/ui/{path:path}")(route_proxy_streamlit_ws)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
    )
