import requests
from unittest.mock import Mock, patch
from openai import OpenAI

from configuration import Albert
from client_albert import ClientAlbert, fabrique_client_albert


def test_peut_fabriquer_un_client_albert_avec_une_configuration_par_defaut():
    client_albert = fabrique_client_albert()

    assert client_albert.client.__class__.__name__ == "OpenAI"
    assert client_albert.session.__class__.__name__ == "ClientAlbertHttp"


def test_pose_question_utilise_le_prompt_comme_messages():
    class Reponse:
        class Message:
            class Content:
                def __init__(self, c: str):
                    self.content = c

            def __init__(self, c: str):
                self.message = Reponse.Message.Content(c)

        def __init__(self, content):
            self.choices = [Reponse.Message(content)]

    QUESTION = "Quelle est la recette de la tartiflette ?"
    REPONSE = "Patates et reblochon"

    FAUX_PARAMETRES_ALBERT = Albert.Parametres(
        modele_reponse="",
        collection_nom_anssi_lab="",
        collection_id_anssi_lab=42,
    )

    mock_client_openai = Mock(OpenAI)
    mock_client_openai.chat.completions.create = Mock(return_value=Reponse(REPONSE))

    mock_client_http = Mock(requests.Session)

    client = ClientAlbert(
        configuration=FAUX_PARAMETRES_ALBERT,
        client_openai=mock_client_openai,
        client_http=mock_client_http,
    )

    with patch("client_albert.ClientAlbert.recherche_paragraphes", return_value={"paragraphes": []}):
        client.pose_question(QUESTION)

        mock_client_openai.chat.completions.create.assert_called_once()

        [args, kwargs] = mock_client_openai.chat.completions.create._mock_call_args
        messages = kwargs["messages"]
        messages_utilisatrice = list(filter(lambda m: m["role"] == "user", messages))

        assert len(messages_utilisatrice) == 1
        assert (
            "Vous êtes un assistant spécialisé dans la cybersécurité et la conformité"
            in messages_utilisatrice[0]["content"]
        )
        assert (QUESTION in messages_utilisatrice[0]["content"])
