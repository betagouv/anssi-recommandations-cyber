import asyncio
import contextlib
import subprocess
import httpx
from fastapi import Request, WebSocket, FastAPI
from fastapi.responses import Response
from contextlib import asynccontextmanager
from config import HOST, ST_PORT, ST_ENTRY


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


async def route_proxy_streamlit_http(request: Request, path: str):
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


async def route_proxy_streamlit_ws(client_ws: WebSocket, path: str):
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
