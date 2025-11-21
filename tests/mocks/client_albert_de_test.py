import requests
from unittest.mock import Mock

from openai import APITimeoutError, OpenAI

from configuration import Albert
from services.albert import (
    ClientAlbertApi,
    ServiceAlbert,
)


class RetourRouteSearch:
    def __init__(self, contenu):
        self._contenu = contenu

    def json(self):
        return {"data": self._contenu}

    def raise_for_status(self):
        pass


class ConstructeurRetourRouteSearch:
    def __init__(self):
        self._retours = []

    def avec_contenu(self, contenu: str):
        self._retours.append(
            {
                "chunk": {"content": contenu},
                "metadata": {"source_url": "", "page": 0, "document_name": ""},
                "score": "0.9",
            }
        )
        return self

    def construis(self) -> RetourRouteSearch:
        return RetourRouteSearch(self._retours)


FAUX_RETOURS_ALBERT_API = (
    ConstructeurRetourRouteSearch().avec_contenu("contenu").construis()
)


class ConstructeurClientHttp:
    def __init__(self):
        self._mock = Mock(requests.Session)

    def qui_retourne(self, retour):
        self._mock.post.return_value = retour
        return self

    def qui_retourne_une_erreur(self, erreur):
        self._mock.post.side_effect = requests.HTTPError(erreur)
        return self

    def qui_timeout(self):
        self._mock.post.side_effect = requests.Timeout("timeout simulé")
        return self

    def construis(self):
        return self._mock


class Reponse:
    class Message:
        class Content:
            def __init__(self, c: str):
                self.content = c

        def __init__(self, c: str):
            self.message = Reponse.Message.Content(c)

    def __init__(self, choix):
        self.choices = choix


class ConstructeurClientOpenai:
    def __init__(self):
        self._mock = Mock(OpenAI)

    def qui_ne_complete_pas(self):
        self._mock.chat.completions.create = Mock(return_value=Reponse([]))
        return self

    def qui_complete_avec(self, reponse):
        self._mock.chat.completions.create = Mock(
            return_value=Reponse([Reponse.Message(reponse)])
        )
        return self

    def qui_timeout(self):
        self._mock.chat.completions.create = Mock(
            side_effect=APITimeoutError(
                "Simulation d'un délai de réponse trop long d'OpenAI."
            )
        )
        return self

    def construis(self):
        return self._mock


class ConstructeurServiceAlbert:
    FAUSSE_CONFIGURATION_ALBERT_CLIENT = Albert.Client(  # type: ignore [attr-defined]
        api_key="",
        base_url="",
        modele_reponse="",
        temps_reponse_maximum_pose_question=10.0,
        temps_reponse_maximum_recherche_paragraphes=1.0,
    )
    FAUSSE_CONFIGURATION_ALBERT_SERVICE = Albert.Service(  # type: ignore [attr-defined]
        collection_nom_anssi_lab="",
        collection_id_anssi_lab=42,
    )
    PROMPT_SYSTEME_ALTERNATIF = (
        "Vous êtes Alberito, un fan d'Albert. Utilisez ces documents:\n\n{chunks}"
    )

    def avec_client_http(self, client_http):
        self._client_http = client_http
        return self

    def avec_client_openai(self, client_openai):
        self._client_openai = client_openai
        return self

    def construis(self):
        mock_client_http = getattr(
            self, "_client_http", ConstructeurClientHttp().construis()
        )
        mock_client_openai = getattr(
            self, "_client_openai", ConstructeurClientOpenai().construis()
        )
        mock_client_albert_api = ClientAlbertApi(
            mock_client_openai,
            mock_client_http,
            self.FAUSSE_CONFIGURATION_ALBERT_CLIENT,
        )

        return ServiceAlbert(
            configuration=self.FAUSSE_CONFIGURATION_ALBERT_SERVICE,
            client=mock_client_albert_api,
            prompt_systeme=self.PROMPT_SYSTEME_ALTERNATIF,
        )
