from question.reclassement.reclassement import Reclasseur, ResultatReclassement
from schemas.albert import Paragraphe, ReclassePayload
from services.client_albert import ClientAlbert


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
