import re
from typing import Protocol

from schemas.albert import Paragraphe, RechercheChunk


BALISE_CONTEXTE_DOCUMENTAIRE = re.compile(
    r"\[Contexte documentaire\].*?\[/Contexte documentaire\]", re.DOTALL
)


class RecuperateurChunksDocument(Protocol):
    def recupere_chunks_document(
        self, identifiant_document: int
    ) -> list[RechercheChunk]: ...


class StrategieEnrichissementParagraphes(Protocol):
    def enrichis(self, paragraphes: list[Paragraphe]) -> list[Paragraphe]: ...


class ParPagePrecedenteEtSuivante:
    def __init__(self, recuperateur_chunks_document: RecuperateurChunksDocument):
        self.recuperateur_chunks_document = recuperateur_chunks_document

    def enrichis(self, paragraphes: list[Paragraphe]) -> list[Paragraphe]:
        chunks_par_document: dict[int, list[RechercheChunk]] = {}
        chunks_deja_inclus_par_document: dict[int, set[tuple[str, int, int | None]]] = {}

        def _enrichis(paragraphe: Paragraphe) -> Paragraphe | None:
            if paragraphe.identifiant_document is None:
                return paragraphe

            identifiant_document = paragraphe.identifiant_document
            if identifiant_document not in chunks_par_document:
                chunks_par_document[identifiant_document] = (
                    self.recuperateur_chunks_document.recupere_chunks_document(
                        identifiant_document
                    )
                )
                chunks_deja_inclus_par_document[identifiant_document] = set()
            chunks_pertinents = [
                chunk
                for chunk in chunks_par_document[identifiant_document]
                if paragraphe.numero_page - 1
                <= chunk.metadata.page
                <= paragraphe.numero_page + 1
            ]
            if not chunks_pertinents:
                return paragraphe

            chunks_uniques = []
            chunks_deja_inclus = chunks_deja_inclus_par_document[identifiant_document]
            for chunk in chunks_pertinents:
                identite_chunk = (
                    chunk.content,
                    chunk.metadata.page,
                    chunk.metadata.position_page,
                )
                if identite_chunk not in chunks_deja_inclus:
                    chunks_uniques.append(chunk)
                    chunks_deja_inclus.add(identite_chunk)
            if not chunks_uniques:
                return None

            chunks_ordonnes = sorted(
                enumerate(chunks_uniques),
                key=lambda element: (
                    element[1].metadata.page,
                    element[1].metadata.position_page is None,
                    element[1].metadata.position_page or 0,
                    element[0],
                ),
            )
            contenu = "\n\n".join(chunk.content for _, chunk in chunks_ordonnes)
            contenu = _conserve_premier_contexte_documentaire(contenu)
            return paragraphe.model_copy(update={"contenu": contenu})

        return [
            paragraphe_enrichi
            for paragraphe in paragraphes
            if (paragraphe_enrichi := _enrichis(paragraphe)) is not None
        ]


def _conserve_premier_contexte_documentaire(contenu: str) -> str:
    contextes = list(BALISE_CONTEXTE_DOCUMENTAIRE.finditer(contenu))
    if len(contextes) <= 1:
        return contenu

    return contenu[: contextes[1].start()] + BALISE_CONTEXTE_DOCUMENTAIRE.sub(
        "", contenu[contextes[1].start() :]
    )
