from typing import Protocol

from schemas.albert import Paragraphe, RechercheChunk


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

        def _enrichis(paragraphe: Paragraphe) -> Paragraphe:
            if paragraphe.identifiant_document is None:
                return paragraphe

            identifiant_document = paragraphe.identifiant_document
            if identifiant_document not in chunks_par_document:
                chunks_par_document[identifiant_document] = (
                    self.recuperateur_chunks_document.recupere_chunks_document(
                        identifiant_document
                    )
                )
            chunks_pertinents = [
                chunk
                for chunk in chunks_par_document[identifiant_document]
                if paragraphe.numero_page - 1
                <= chunk.metadata.page
                <= paragraphe.numero_page + 1
            ]
            if not chunks_pertinents:
                return paragraphe

            chunks_ordonnes = sorted(
                enumerate(chunks_pertinents),
                key=lambda element: (
                    element[1].metadata.page,
                    element[1].metadata.position_page is None,
                    element[1].metadata.position_page or 0,
                    element[0],
                ),
            )
            contenu = "\n\n".join(chunk.content for _, chunk in chunks_ordonnes)
            return paragraphe.model_copy(update={"contenu": contenu})

        return [_enrichis(paragraphe) for paragraphe in paragraphes]
