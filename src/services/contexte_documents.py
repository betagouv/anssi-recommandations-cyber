import html
import re

from schemas.albert import Paragraphe
from schemas.msc import ContexteDocumentMSC, ReponseGuideMSC


def texte_visible_description(description: str) -> str:
    sans_scripts = re.sub(
        r"<(script|style)\b.*?</\1>", "", description, flags=re.DOTALL | re.IGNORECASE
    )
    texte = html.unescape(re.sub(r"<[^>]*>", " ", sans_scripts))
    return re.sub(r"\s+", " ", texte).strip()


def associe_contexte_msc(
    paragraphes: list[Paragraphe], guides: list[ReponseGuideMSC]
) -> list[Paragraphe]:
    guides_par_document: dict[str, list[ReponseGuideMSC]] = {}
    for guide in guides:
        for document in guide.listeDocuments:
            guides_par_document.setdefault(document.nomFichier, []).append(guide)

    def contexte(paragraphe: Paragraphe) -> ContexteDocumentMSC | None:
        correspondants = guides_par_document.get(paragraphe.nom_document, [])
        if len(correspondants) != 1:
            return None
        return ContexteDocumentMSC(
            nom=correspondants[0].nom,
            description=texte_visible_description(correspondants[0].description),
        )

    return [
        paragraphe.model_copy(update={"contexte_document_msc": contexte(paragraphe)})
        for paragraphe in paragraphes
    ]
