import logging
import os
from collections.abc import Callable
from typing import Any, Coroutine

import requests
from fastmcp import FastMCP
from fastmcp.server.auth import TokenVerifier
from fastmcp.server.auth.providers.jwt import JWTVerifier
from pydantic import AnyHttpUrl, TypeAdapter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SCOPE_POSE_QUESTION = "question:poser"
ADAPTATEUR_URL_HTTP = TypeAdapter(AnyHttpUrl)

AppelleAPIConversation = Callable[[str, str], Coroutine[Any, Any, dict[str, Any]]]


def fabrique_serveur_mcp(
    *,
    api_base_url: str | None = None,
    appelle_api_conversation: AppelleAPIConversation,
    token_verifier: TokenVerifier,
) -> FastMCP:
    api_base_url_mcp = (
        api_base_url
        if api_base_url is not None
        else os.getenv("MCP_API_BASE_URL", "http://127.0.0.1:3001")
    ).rstrip("/")

    serveur_mcp = FastMCP(
        name="Recommandations Cyber",
        auth=token_verifier,
    )

    @serveur_mcp.tool(
        name="pose_question",
        description="Pose une question cyber à l'API Recommandations Cyber.",
    )
    async def pose_question(question: str) -> dict[str, Any]:
        return await appelle_api_conversation(question, api_base_url_mcp)

    return serveur_mcp


async def appel_mqc(question: str, api_base_url: str) -> dict[str, Any]:
    session = requests.Session()
    reponse = session.post(
        f"{api_base_url}/api/conversation", json={"question": question}
    )
    reponse.raise_for_status()
    return reponse.json()


if __name__ == "__main__":
    hote = "127.0.0.1"
    port = 8001
    api_base_url = "http://127.0.0.1:3001"

    logger.info("Démarrage du serveur MCP…")

    fabrique_serveur_mcp(
        api_base_url=api_base_url,
        appelle_api_conversation=appel_mqc,
        token_verifier=JWTVerifier(
            public_key=os.getenv("MCP_CLEF_JWT"),
            issuer="internal-auth-service",
            audience="mcp-internal-api",
            algorithm="HS256",
        ),
    ).run(transport="http", host=hote, port=port)
