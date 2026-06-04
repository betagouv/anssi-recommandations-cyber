import logging
import os
from collections.abc import Callable
from typing import Any, Coroutine, TypedDict

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
    api_base_url: str,
    appelle_api_conversation: AppelleAPIConversation,
    token_verifier: TokenVerifier,
) -> FastMCP:
    api_base_url_mcp = api_base_url.rstrip("/")

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


class VariablesEnvironnementNecessaires(TypedDict):
    URL_MQC: str
    PORT_MQC: str
    MCP_HOST: str
    MCP_PORT: int
    MCP_CLEF_JWT: str


def _les_variables_d_environnement() -> VariablesEnvironnementNecessaires:
    env_mcp_port = os.getenv("MCP_PORT")
    variables_environnement: dict[str, str | int | None] = {
        "URL_MQC": os.getenv("URL_MQC"),
        "PORT_MQC": os.getenv("PORT_MQC"),
        "MCP_HOST": os.getenv("MCP_HOST"),
        "MCP_PORT": int(env_mcp_port) if env_mcp_port else None,
        "MCP_CLEF_JWT": os.getenv("MCP_CLEF_JWT"),
    }
    return variables_environnement  # type: ignore


def _verifie_la_presence_des_variables_d_environnement_necessaires() -> (
    VariablesEnvironnementNecessaires
):
    variables_environnement = _les_variables_d_environnement()
    variables_manquantes = list(
        filter(lambda x: x[1] is None, variables_environnement.items())
    )
    cles_manquantes = list(map(lambda x: x[0], variables_manquantes))
    if len(cles_manquantes) > 0:
        raise Exception(
            f"Les variables d'environnement suivantes sont manquantes :\n - {'\n - '.join(cles_manquantes)}"
        )
    return variables_environnement  # type: ignore


if __name__ == "__main__":
    _verifie_la_presence_des_variables_d_environnement_necessaires()
    variables_environnement = _les_variables_d_environnement()
    url_mqc = variables_environnement["URL_MQC"]
    port_mqc = variables_environnement["PORT_MQC"]
    hote_mcp = variables_environnement["MCP_HOST"]
    port_mcp = variables_environnement["MCP_PORT"]
    api_base_url = f"{url_mqc}:{port_mqc}"

    logger.info("Démarrage du serveur MCP…")

    fabrique_serveur_mcp(
        api_base_url=api_base_url,
        appelle_api_conversation=appel_mqc,
        token_verifier=JWTVerifier(
            public_key=variables_environnement["MCP_CLEF_JWT"],
            issuer="internal-auth-service",
            audience="mcp-internal-api",
            algorithm="HS256",
        ),
    ).run(transport="http", host=hote_mcp, port=port_mcp)
