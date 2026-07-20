import json
from abc import ABC, abstractmethod
from openai.types.chat import ChatCompletionMessageParam
from typing import NamedTuple, cast

from schemas.albert import Paragraphe, ReclassePayload
from services.client_albert import ClientAlbert


class ResultatReclassement(NamedTuple):
    paragraphes_retenus: list[Paragraphe]
    tous_les_candidats: list[Paragraphe]
    aucune_source_utile: bool = False


class Reclasseur(ABC):
    @abstractmethod
    def reclasse(
        self, question: str, paragraphes: list[Paragraphe]
    ) -> ResultatReclassement:
        pass


class ReclasseurBGE(Reclasseur):
    def __init__(
        self,
        client: ClientAlbert,
        modele: str,
        prompt: str,
        nombre_paragraphes: int,
    ) -> None:
        self.client = client
        self.modele = modele
        self.prompt = prompt
        self.nombre_paragraphes = nombre_paragraphes

    def reclasse(
        self, question: str, paragraphes: list[Paragraphe]
    ) -> ResultatReclassement:
        payload = ReclassePayload(
            query=self.prompt.format(QUESTION=question),
            documents=[p.contenu for p in paragraphes],
            model=self.modele,
        )
        reclassement = self.__reclasse_payload(payload)
        contenus_tries = reclassement["paragraphes_tries"]
        scores_tries = reclassement["scores_tries"]

        if not contenus_tries:
            return ResultatReclassement(
                paragraphes_retenus=paragraphes[: self.nombre_paragraphes],
                tous_les_candidats=paragraphes,
            )

        paragraphes_tries = [
            next(p for p in paragraphes if p.contenu == contenu).model_copy(
                update={"score_reclassement": score}
            )
            for contenu, score in zip(contenus_tries, scores_tries)
        ]
        return ResultatReclassement(
            paragraphes_retenus=paragraphes_tries[: self.nombre_paragraphes],
            tous_les_candidats=paragraphes_tries,
        )

    def __reclasse_payload(self, payload: ReclassePayload) -> dict[str, list]:
        resultat = self.client.reclasse(payload)
        donnees = sorted(resultat.data, key=lambda data: data.score, reverse=True)
        return {
            "paragraphes_tries": [payload.documents[data.index] for data in donnees],
            "scores_tries": [data.score for data in donnees],
        }


class ReclasseurLLM(Reclasseur):
    _CATEGORIE_RETENUE = "preuve_principale"
    _SCORE_PREUVE_PRINCIPALE = 1.0

    def __init__(self, client: ClientAlbert, prompt: str) -> None:
        self.client = client
        self.prompt = prompt

    def reclasse(
        self, question: str, paragraphes: list[Paragraphe]
    ) -> ResultatReclassement:
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": self.prompt.format(
                    QUESTION=question,
                    CANDIDATS=self._formate_candidats(paragraphes),
                ),
            }
        ]
        propositions = self.client.recupere_propositions(messages, temperature=0)
        contenu = cast(str, propositions[0].message.content)
        resultat = json.loads(contenu)
        categories = {
            evaluation["id"]: evaluation["categorie"]
            for evaluation in resultat["evaluations"]
        }
        paragraphes_par_id = {
            identifiant: p for identifiant, p in enumerate(paragraphes, 1)
        }
        paragraphes_retenus = [
            paragraphes_par_id[identifiant].model_copy(
                update={"score_reclassement": self._SCORE_PREUVE_PRINCIPALE}
            )
            for identifiant in resultat["ids_retenus"]
            if categories[identifiant] == self._CATEGORIE_RETENUE
        ]
        return ResultatReclassement(
            paragraphes_retenus=paragraphes_retenus,
            tous_les_candidats=paragraphes,
            aucune_source_utile=not paragraphes_retenus,
        )

    @staticmethod
    def _formate_candidats(paragraphes: list[Paragraphe]) -> str:
        return "\n\n".join(
            (
                f"[PASSAGE id={identifiant} rang_initial={p.rang_initial} "
                f"document={p.nom_document!r} "
                f"page={p.numero_page} score_initial={p.score_similarite}]\n"
                f"{p.contenu}\n[/PASSAGE]"
            )
            for identifiant, p in enumerate(paragraphes, 1)
        )
