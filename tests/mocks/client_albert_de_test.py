import random
from typing import NamedTuple, Optional
from unittest.mock import Mock
import requests
from openai import APITimeoutError, OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice, ChatCompletionMessage
from schemas.albert import (
    RecherchePayload,
    ResultatRecherche,
    ResultatRechercheJeopardy,
    RechercheChunk,
    RechercheMetadonnees,
    ReclasseReponse,
    ReclassePayload,
    ResultatReclasse,
)
from services.client_albert import ClientAlbert
from services.exceptions import ErreurRechercheDocuments


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


class RetourRouteRerank:
    def __init__(self, resultats: list[dict]):
        self._resultats = resultats

    def json(self):
        return {"results": self._resultats}

    def raise_for_status(self):
        pass


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


class ClientAlbertMemoire(ClientAlbert):
    def __init__(self):
        self.payload_reclassement_recu = None
        self.reclassement = ReclasseReponse(id="1", object="list", data=[])
        self.propositions_vides = False
        self.resultats_vides = False
        self.leve_une_erreur_sur_recherche = False
        self.messages_recus = []
        self.payload_recu = None
        self.resultats = []
        self.choix = []
        self.resultats_jeopardy = []
        self.payload_jeopardy_recu = None
        self.appels_recherche = 0
        self.resultats_par_appel = []
        self.chunks_par_id = []
        self.appels_recherche_chunk_par_id = []
        self.document_id_recu = None
        self.chunk_id_recu = None

    def recherche(self, payload: RecherchePayload) -> list[ResultatRecherche]:
        self.payload_recu = payload
        if self.leve_une_erreur_sur_recherche:
            raise ErreurRechercheDocuments(
                "Une erreur est survenue lors de la recherche des guides de l'ANSSI."
            )

        if self.resultats_par_appel:
            resultat = (
                self.resultats_par_appel[self.appels_recherche]
                if self.appels_recherche < len(self.resultats_par_appel)
                else []
            )
            self.appels_recherche += 1
            return resultat

        return self.resultats if self.resultats_vides is False else []

    def recherche_jeopardy(
        self, payload: RecherchePayload
    ) -> list[ResultatRechercheJeopardy]:
        self.payload_jeopardy_recu = payload
        return self.resultats_jeopardy

    def recherche_chunk_par_id(
        self, document_id: str, chunk_id: int
    ) -> ResultatRecherche:
        self.document_id_recu = document_id
        self.chunk_id_recu = chunk_id
        self.appels_recherche_chunk_par_id.append((document_id, chunk_id))
        if self.chunks_par_id:
            return self.chunks_par_id.pop(0)
        return un_resultat_de_recherche().construis()

    def recupere_propositions(
        self, messages: list[ChatCompletionMessageParam], modele: str | None = None
    ) -> list[Choice]:
        self.messages_recus = messages
        return self.choix if self.propositions_vides is False else []

    def reclasse(self, payload: ReclassePayload) -> ReclasseReponse:
        self.payload_reclassement_recu = payload
        return self.reclassement

    def avec_les_resultats(self, resultats: list[ResultatRecherche]):
        self.resultats.extend(resultats)

    def avec_les_resultats_par_appel(
        self, resultats_par_appel: list[list[ResultatRecherche]]
    ):
        self.resultats_par_appel = resultats_par_appel

    def avec_les_resultats_jeopardy(self, resultats: list[ResultatRechercheJeopardy]):
        self.resultats_jeopardy.extend(resultats)

    def avec_chunk_par_id(self, chunk: ResultatRecherche):
        self.chunks_par_id.append(chunk)

    def avec_chunks_par_id(self, chunks: list[ResultatRecherche]):
        self.chunks_par_id.extend(chunks)

    def avec_les_propositions(self, choix: list[Choice]):
        self.choix.extend(choix)

    def qui_leve_une_erreur_sur_recherche(self):
        self.leve_une_erreur_sur_recherche = True

    def sans_resultats(self):
        self.resultats_vides = True

    def sans_propositions(self):
        self.propositions_vides = True

    def avec_le_reclassement(self, reclassement: ReclasseReponse):
        resultats_recherche = list(
            map(
                lambda r: un_resultat_de_recherche()
                .ayant_pour_contenu(f"paragraphe {r.index}")
                .construis(),
                reclassement.data,
            )
        )
        self.resultats.extend(resultats_recherche)
        self.reclassement = reclassement

    def reclassement_vide(self):
        self.reclassement = ReclasseReponse(data=[])


class ConstructeurResultatDeRecherche:
    def __init__(self):
        self.contenu = "Un contenu"
        self.id_reponse: Optional[str] = None

    def ayant_pour_contenu(self, contenu: str):
        self.contenu = contenu
        return self

    def ayant_reponse_maitrisee(self, id_reponse: str):
        self.id_reponse = id_reponse
        return self

    def construis(self) -> ResultatRecherche:
        return ResultatRecherche(
            RechercheChunk(
                content=self.contenu,
                metadata=RechercheMetadonnees(
                    source_url="", page=1, nom_document="", id_reponse=self.id_reponse
                ),
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


class ParagraphesLesMieuxClasses(NamedTuple):
    titre: str
    indice: int
    score: float


class ConstructeurDeReponseDeReclassement:
    def __init__(self):
        self.paragraphes_les_mieux_classes = []
        self.paragraphes = []

    def avec_les_paragraphes_les_mieux_classes(
        self, paragraphes: list[ParagraphesLesMieuxClasses]
    ):
        self.paragraphes_les_mieux_classes.extend(paragraphes)
        return self

    def avec_5_resultats(self, paragraphes: list[ParagraphesLesMieuxClasses]):
        self.paragraphes = paragraphes
        return self

    def construis(self) -> ReclasseReponse:
        def _calcule_score_faible() -> float:
            return random.uniform(0.0, 0.6)

        data = []
        if len(self.paragraphes) > 0:
            for paragraphe in self.paragraphes:
                resultat = ResultatReclasse(
                    object="rerank",
                    score=paragraphe["score"],
                    index=paragraphe["indice"],
                )
                data.append(resultat)
            return ReclasseReponse(
                data=data,
            )

        for i in range(0, 20):
            paragraphe = next(
                (p for p in self.paragraphes_les_mieux_classes if p["indice"] == i),
                None,
            )
            if paragraphe is not None:
                resultat = ResultatReclasse(
                    object="rerank", score=paragraphe["score"], index=i
                )

            else:
                resultat = ResultatReclasse(
                    object="rerank", score=_calcule_score_faible(), index=i
                )
            data.append(resultat)

        return ReclasseReponse(
            data=data,
        )


def un_resultat_de_recherche() -> ConstructeurResultatDeRecherche:
    return ConstructeurResultatDeRecherche()


def un_choix_de_proposition() -> ConstructeurDeChoix:
    return ConstructeurDeChoix()


def un_constructeur_de_reponse_de_reclassement() -> ConstructeurDeReponseDeReclassement:
    return ConstructeurDeReponseDeReclassement()
