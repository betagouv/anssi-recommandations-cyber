import pytest
import requests
from unittest.mock import Mock, patch
from openai import OpenAI

from configuration import Albert
from client_albert import ClientAlbert, fabrique_client_albert
from schemas.reponses import Paragraphe


def test_peut_fabriquer_un_client_albert_avec_une_configuration_par_defaut():
    client_albert = fabrique_client_albert()

    assert client_albert.client.__class__.__name__ == "OpenAI"
    assert client_albert.session.__class__.__name__ == "ClientAlbertHttp"
    assert (
        "Vous êtes un assistant spécialisé dans la cybersécurité et la conformité"
        in client_albert.PROMPT_SYSTEM
    )


PROMPT_SYSTEME_ALTERNATIF = (
    "Vous êtes Alberito, un fan d'Albert. Utilisez ces documents:\n\n{chunks}"
)
QUESTION = "Quelle est la recette de la tartiflette ?"
REPONSE = "Patates et reblochon"


@pytest.fixture
def mock_client_openai():
    class Reponse:
        class Message:
            class Content:
                def __init__(self, c: str):
                    self.content = c

            def __init__(self, c: str):
                self.message = Reponse.Message.Content(c)

        def __init__(self, content):
            self.choices = [Reponse.Message(content)]

    mock_client_openai = Mock(OpenAI)
    mock_client_openai.chat.completions.create = Mock(return_value=Reponse(REPONSE))
    return mock_client_openai


@pytest.fixture
def mock_client_http():
    return Mock(requests.Session)


@pytest.fixture
def client(mock_client_openai, mock_client_http):
    FAUX_PARAMETRES_ALBERT = Albert.Parametres(
        modele_reponse="",
        collection_nom_anssi_lab="",
        collection_id_anssi_lab=42,
    )

    return ClientAlbert(
        configuration=FAUX_PARAMETRES_ALBERT,
        client_openai=mock_client_openai,
        client_http=mock_client_http,
        prompt_systeme=PROMPT_SYSTEME_ALTERNATIF,
    )


def test_pose_question_separe_la_question_de_l_utilisatrice_des_instructions_systeme(
    client, mock_client_openai
):
    with patch(
        "client_albert.ClientAlbert.recherche_paragraphes",
        return_value={"paragraphes": []},
    ):
        client.pose_question(QUESTION)

        mock_client_openai.chat.completions.create.assert_called_once()

        [args, kwargs] = mock_client_openai.chat.completions.create._mock_call_args
        messages = kwargs["messages"]
        messages_systeme = list(filter(lambda m: m["role"] == "system", messages))
        messages_utilisatrice = list(filter(lambda m: m["role"] == "user", messages))

        bout_de_prompt_systeme = PROMPT_SYSTEME_ALTERNATIF.split("\n\n")[0]
        assert len(messages_systeme) == 1
        assert bout_de_prompt_systeme in messages_systeme[0]["content"]
        assert len(messages_utilisatrice) == 1
        assert QUESTION in messages_utilisatrice[0]["content"]


def test_pose_question_les_documents_sont_ajoutes_aux_instructions_systeme(
    client, mock_client_openai
):
    FAUX_CONTENU = "La tartiflette est une recette de cuisine à base de gratin de pommes de terre, d'oignons et de lardons, le tout gratiné au reblochon."
    FAUX_DOCUMENTS = {
        "paragraphes": [
            Paragraphe(
                score_similarite=0.5,
                numero_page=1,
                url="https://cyber.gouv.fr/document.pdf",
                nom_document="Mon Guide Cyber",
                contenu=FAUX_CONTENU,
            )
        ]
    }

    with patch(
        "client_albert.ClientAlbert.recherche_paragraphes", return_value=FAUX_DOCUMENTS
    ):
        client.pose_question(QUESTION)

        mock_client_openai.chat.completions.create.assert_called_once()

        [args, kwargs] = mock_client_openai.chat.completions.create._mock_call_args
        messages = kwargs["messages"]
        messages_systeme = list(filter(lambda m: m["role"] == "system", messages))

        assert len(messages_systeme) == 1
        assert FAUX_CONTENU in messages_systeme[0]["content"]
