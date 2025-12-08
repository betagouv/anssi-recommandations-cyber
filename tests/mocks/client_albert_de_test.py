import requests
from unittest.mock import Mock

from openai import APITimeoutError, OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice, ChatCompletionMessage

from configuration import Albert
from infra.albert.client_albert import (
    ClientAlbertApi,
)
from schemas.albert import (
    RecherchePayload,
    ResultatRecherche,
    RechercheChunk,
    RechercheMetadonnees,
)
from services.service_albert import ServiceAlbert, ClientAlbert


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
        utilise_recherche_hybride=False,
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
            utilise_recherche_hybride=self.FAUSSE_CONFIGURATION_ALBERT_CLIENT.utilise_recherche_hybride,
        )


class ClientAlbertMemoire(ClientAlbert):
    def __init__(self):
        self.propositions_vides = False
        self.resultats_vides = False
        self.messages_recus = []
        self.payload_recu = None
        self.resultats = []
        self.choix = []

    def recherche(self, payload: RecherchePayload) -> list[ResultatRecherche]:
        self.payload_recu = payload
        return self.resultats if self.resultats_vides is False else []

    def recupere_propositions(
        self, messages: list[ChatCompletionMessageParam]
    ) -> list[Choice]:
        self.messages_recus = messages
        return self.choix if self.propositions_vides is False else []

    def avec_les_resultats(self, resultats: list[ResultatRecherche]):
        self.resultats.extend(resultats)

    def avec_les_propositions(self, choix: list[Choice]):
        self.choix.extend(choix)

    def sans_resultats(self):
        self.resultats_vides = True

    def sans_propositions(self):
        self.propositions_vides = True


class ConstructeurResultatDeRecherche:
    def __init__(self):
        self.contenu = "Un contenu"

    def ayant_pour_contenu(self, contenu: str):
        self.contenu = contenu
        return self

    def construis(self) -> ResultatRecherche:
        return ResultatRecherche(
            RechercheChunk(
                content=self.contenu,
                metadata=RechercheMetadonnees(source_url="", page=1, nom_document=""),
            ),
            0.5,
        )


class ConstructeurDeChoix:
    def __init__(self):
        self.contenu = "Un contenu"

    def ayant_pour_contenu(self, contenu: str):
        self.contenu = contenu
        return self

    def construis(self) -> Choice:
        return Choice(
            message=ChatCompletionMessage(content=self.contenu, role="assistant"),
            finish_reason="stop",
            index=1,
        )


def un_resultat_de_recherche() -> ConstructeurResultatDeRecherche:
    return ConstructeurResultatDeRecherche()


def un_choix_de_proposition() -> ConstructeurDeChoix:
    return ConstructeurDeChoix()
