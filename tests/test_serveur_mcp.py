import pytest
from fastmcp import FastMCP
from fastmcp.server.auth import StaticTokenVerifier, AuthProvider
from fastmcp.tools import Tool

from serveur_mcp import (
    fabrique_serveur_mcp,
)


async def un_appel_api_conversation(
    question: str, api_base_url: str
) -> dict[str, object]:
    return {
        "question": question,
        "api_base_url": api_base_url,
        "reponse": "Reponse de test",
    }


def un_serveur_mcp_http(
    *,
    token="jeton-secret",
    api_base_url="http://api.test",
    appelle_api_conversation=un_appel_api_conversation,
) -> FastMCP:
    serveur_mcp = fabrique_serveur_mcp(
        api_base_url=api_base_url,
        appelle_api_conversation=appelle_api_conversation,
        token_verifier=StaticTokenVerifier(
            tokens={
                token: {
                    "client_id": "mqc@company.com",
                    "scopes": ["read:data", "write:data", "admin:users"],
                }
            }
        ),
    )
    return serveur_mcp


@pytest.mark.asyncio
async def test_serveur_mcp_http_refuse_les_requetes_sans_bon_jeton() -> None:
    serveur_mcp = un_serveur_mcp_http(token="jeton-secret")
    autentification: AuthProvider | None = serveur_mcp.auth

    assert autentification is not None
    assert await autentification.verify_token("mauvais-jeton") is None


@pytest.mark.asyncio
async def test_serveur_mcp_http_expose_l_outil_pose_question() -> None:
    serveur_mcp = un_serveur_mcp_http(
        token="jeton-secret",
        api_base_url="http://api.test",
        appelle_api_conversation=un_appel_api_conversation,
    )

    outil: Tool | None = await serveur_mcp.get_tool("pose_question")

    assert outil is not None
