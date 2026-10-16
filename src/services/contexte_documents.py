from html.parser import HTMLParser
import re

from schemas.albert import Paragraphe
from schemas.msc import ContexteDocumentMSC, ReponseGuideMSC


def associe_contexte_msc(
    paragraphes: list[Paragraphe], guides: list[ReponseGuideMSC]
) -> list[Paragraphe]:
    associations: dict[str, list[ReponseGuideMSC]] = {}
    for guide in guides:
        for document in guide.listeDocuments:
            associations.setdefault(document.nomFichier, []).append(guide)

    resultat = []
    for paragraphe in paragraphes:
        guides_correspondants = associations.get(paragraphe.nom_document, [])
        contexte = None
        if len(guides_correspondants) == 1:
            guide = guides_correspondants[0]
            contexte = ContexteDocumentMSC(
                nom=guide.nom,
                description=guide.description,
                nom_fichier=paragraphe.nom_document,
            )
        resultat.append(
            paragraphe.model_copy(update={"contexte_document_msc": contexte})
        )
    return resultat


class _ExtracteurTexteDescription(HTMLParser):
    _BALISES_BLOC = {
        "address",
        "article",
        "blockquote",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "figure",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "main",
        "ol",
        "p",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.fragments: list[str] = []
        self._balises_invisibles: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self._balises_invisibles.append(tag)
        elif tag == "br":
            self.fragments.append("\n")
        elif tag in self._BALISES_BLOC:
            self.fragments.append("\n- " if tag == "li" else "\n\n")

    def handle_endtag(self, tag: str) -> None:
        if self._balises_invisibles and tag == self._balises_invisibles[-1]:
            self._balises_invisibles.pop()
        elif tag == "li":
            return
        elif tag in self._BALISES_BLOC:
            self.fragments.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._balises_invisibles:
            self.fragments.append(data)


def texte_visible_description(description: str) -> str:
    extracteur = _ExtracteurTexteDescription()
    extracteur.feed(description)
    extracteur.close()
    texte = "".join(extracteur.fragments)
    texte = re.sub(r"[\t\f\v ]+", " ", texte)
    texte = re.sub(r" *\n *", "\n", texte)
    texte = re.sub(r"\n{3,}", "\n\n", texte)
    return texte.strip()
