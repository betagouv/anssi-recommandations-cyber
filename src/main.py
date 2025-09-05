import uvicorn
from fastapi import FastAPI, Depends, Request
from typing import Dict
from client_albert import ClientAlbert
from schemas.requetes import QuestionRequete
from config import HOST, PORT, ST_ENTRY, ST_PORT
from schemas.reponses import ReponseQuestion
from contextlib import asynccontextmanager
import subprocess
import httpx
import asyncio, contextlib
from fastapi import WebSocket
from fastapi.responses import Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.st_proc = subprocess.Popen(
        [
            "streamlit",
            "run",
            ST_ENTRY,
            "--server.port",
            str(ST_PORT),
            "--server.address",
            HOST,
            "--server.baseUrlPath",
            "ui",
            "--browser.gatherUsageStats",
            "false",
        ]
    )
    yield
    if (
        hasattr(app.state, "st_proc")
        and app.state.st_proc
        and app.state.st_proc.poll() is None
    ):
        app.state.st_proc.terminate()


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


@app.api_route(
    "/ui/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
)
async def proxy_streamlit_http(request: Request, path: str):
    """Proxy HTTP vers Streamlit.

    Redirige toutes les requêtes /ui/* vers Streamlit pour avoir une seule URL d'accès.
    Permet d'éviter les problèmes CORS et de simplifier le déploiement (un seul port exposé).
    """
    target = f"http://{HOST}:{ST_PORT}/ui/{path}"
    body = await request.body()
    headers = dict(request.headers)
    headers["host"] = f"{HOST}:{ST_PORT}"
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        resp = await client.request(
            request.method, target, content=body, headers=headers
        )
    hop = {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }
    out_headers = {k: v for k, v in resp.headers.items() if k.lower() not in hop}
    return Response(resp.content, status_code=resp.status_code, headers=out_headers)


@app.websocket("/ui/{path:path}")
async def proxy_streamlit_ws(client_ws: WebSocket, path: str):
    """Proxy WebSocket vers Streamlit.

    Nécessaire pour la communication temps réel de Streamlit (auto-refresh, interactions).
    Sans ce proxy, l'interface Streamlit ne pourrait pas se mettre à jour dynamiquement.
    """
    await client_ws.accept()
    import websockets

    uri = f"ws://{HOST}:{ST_PORT}/ui/{path}"
    async with websockets.connect(uri) as server_ws:

        async def client_vers_serveur():
            while True:
                data = await client_ws.receive_bytes()
                await server_ws.send(data)

        async def serveur_vers_client():
            while True:
                data = await server_ws.recv()
                if isinstance(data, bytes):
                    await client_ws.send_bytes(data)
                else:
                    await client_ws.send_text(data)

        try:
            await asyncio.gather(client_vers_serveur(), serveur_vers_client())
        finally:
            with contextlib.suppress(Exception):
                await client_ws.close()
            with contextlib.suppress(Exception):
                await server_ws.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
    )
