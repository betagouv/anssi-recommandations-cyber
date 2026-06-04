from typing import cast

import pytest
import uuid
from fastmcp import FastMCP
from fastmcp.server.auth import StaticTokenVerifier, AuthProvider
from fastmcp.tools import Tool

from serveur_mcp import (
    fabrique_serveur_mcp,
    ReponseMQC,
)


async def un_appel_api_conversation(
    _api_base_url: str, question: str, id_conversation: uuid.UUID | None = None
) -> ReponseMQC:
    return ReponseMQC(
        reponse="Réponse de test",
        question=question,
        id_conversation=uuid.uuid4() if id_conversation is None else id_conversation,
        id_interaction=uuid.uuid4(),
        paragraphes=[],
    )


async def un_appel_api_conversation_avec_une_interaction(
    _api_base_url: str, question: str, id_conversation: uuid.UUID | None = None
) -> ReponseMQC:
    return ReponseMQC(
        reponse="Réponse de test d’interaction",
        question=question,
        id_conversation=None,
        id_interaction=uuid.uuid4(),
        paragraphes=[],
    )


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


@pytest.mark.asyncio
async def test_serveur_mcp_http_expose_l_outil_pose_question_en_engageant_une_conversation() -> (
    None
):
    serveur_mcp = un_serveur_mcp_http(
        token="jeton-secret",
        api_base_url="http://api.test",
        appelle_api_conversation=un_appel_api_conversation,
    )

    outil: Tool = cast(Tool, await serveur_mcp.get_tool("pose_question"))
    reponse = await outil.run({"question": "Quel est la question ?"})

    assert reponse.structured_content["reponse"] == "Réponse de test"  # type: ignore [index]
    assert reponse.structured_content["id_conversation"] is not None  # type: ignore [index]


@pytest.mark.asyncio
async def test_serveur_mcp_http_expose_l_outil_pose_question_en_continuant_une_conversation() -> (
    None
):
    serveur_mcp = un_serveur_mcp_http(
        token="jeton-secret",
        api_base_url="http://api.test",
        appelle_api_conversation=un_appel_api_conversation,
    )
    id_conversation = uuid.uuid4()

    outil: Tool = cast(Tool, await serveur_mcp.get_tool("pose_question"))
    reponse = await outil.run(
        {"question": "Quel est la question ?", "id_conversation": id_conversation}
    )

    assert reponse.structured_content["reponse"] == "Réponse de test"  # type: ignore [index]
    assert reponse.structured_content["id_conversation"] == str(id_conversation)  # type: ignore [index]


@pytest.mark.asyncio
async def test_serveur_mcp_http_expose_l_outil_pose_question_meme_si_l_identifiant_de_la_conversation_n_est_pas_retourne() -> (
    None
):
    serveur_mcp = un_serveur_mcp_http(
        token="jeton-secret",
        api_base_url="http://api.test",
        appelle_api_conversation=un_appel_api_conversation_avec_une_interaction,
    )
    id_conversation = uuid.uuid4()

    outil: Tool = cast(Tool, await serveur_mcp.get_tool("pose_question"))
    reponse = await outil.run(
        {"question": "Quel est la question ?", "id_conversation": id_conversation}
    )

    assert reponse.structured_content["reponse"] == "Réponse de test d’interaction"  # type: ignore [index]
    assert reponse.structured_content["id_conversation"] is None  # type: ignore [index]
