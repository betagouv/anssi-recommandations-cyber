from schemas.albert import Paragraphe, RechercheChunk, RechercheMetadonnees
from services.strategie_enrichissement_paragraphes import (
    ParPagePrecedenteEtSuivante,
)


class RecuperateurChunksDocumentMemoire:
    def __init__(self, chunks: list[RechercheChunk]):
        self.chunks = chunks
        self.identifiants_documents_recus: list[int] = []

    def recupere_chunks_document(self, identifiant_document: int) -> list[RechercheChunk]:
        self.identifiants_documents_recus.append(identifiant_document)
        return self.chunks


def test_enrichit_un_paragraphe_avec_les_pages_precedente_courante_et_suivante():
    recuperateur = RecuperateurChunksDocumentMemoire(
        [
            RechercheChunk(
                content="Page 4, position 0",
                metadata=RechercheMetadonnees(source_url="", page=4, nom_document=""),
            ),
            RechercheChunk(
                content="Page 3, position 1",
                metadata=RechercheMetadonnees(
                    source_url="", page=3, nom_document="", position_page=1
                ),
            ),
            RechercheChunk(
                content="Page 2, position 0",
                metadata=RechercheMetadonnees(
                    source_url="", page=2, nom_document="", position_page=0
                ),
            ),
            RechercheChunk(
                content="Page 3, position 0",
                metadata=RechercheMetadonnees(
                    source_url="", page=3, nom_document="", position_page=0
                ),
            ),
        ]
    )
    paragraphe = Paragraphe(
        contenu="Contenu source",
        url="https://exemple.fr/document.pdf",
        score_similarite=0.9,
        numero_page=3,
        nom_document="document.pdf",
        identifiant_document=4777455,
    )

    resultat = ParPagePrecedenteEtSuivante(recuperateur).enrichis([paragraphe])

    assert resultat[0].contenu == (
        "Page 2, position 0\n\n"
        "Page 3, position 0\n\n"
        "Page 3, position 1\n\n"
        "Page 4, position 0"
    )


def test_enrichit_un_paragraphe_en_ne_conservant_que_le_premier_contexte_documentaire():
    recuperateur = RecuperateurChunksDocumentMemoire(
        [
            RechercheChunk(
                content=(
                    "[Contexte documentaire]\n"
                    "Document : guide.pdf\n"
                    "Sections : Paragraphe 1\n"
                    "[/Contexte documentaire]\n\n"
                    "Le contenu du paragraphe 1"
                ),
                metadata=RechercheMetadonnees(source_url="", page=2, nom_document=""),
            ),
            RechercheChunk(
                content=(
                    "[Contexte documentaire]\n"
                    "Document : guide.pdf\n"
                    "Sections : Paragraphe 2\n"
                    "[/Contexte documentaire]\n\n"
                    "Le contenu du paragraphe 2"
                ),
                metadata=RechercheMetadonnees(source_url="", page=3, nom_document=""),
            ),
        ]
    )
    paragraphe = Paragraphe(
        contenu="Contenu source",
        url="https://exemple.fr/document.pdf",
        score_similarite=0.9,
        numero_page=2,
        nom_document="document.pdf",
        identifiant_document=4777455,
    )

    resultat = ParPagePrecedenteEtSuivante(recuperateur).enrichis([paragraphe])

    assert resultat[0].contenu == (
        "[Contexte documentaire]\n"
        "Document : guide.pdf\n"
        "Sections : Paragraphe 1\n"
        "[/Contexte documentaire]\n\n"
        "Le contenu du paragraphe 1\n\n\n\n"
        "Le contenu du paragraphe 2"
    )


def test_ne_lit_qu_une_fois_un_document_partage_par_plusieurs_paragraphes():
    recuperateur = RecuperateurChunksDocumentMemoire(
        [
            RechercheChunk(
                content="Contenu page 3",
                metadata=RechercheMetadonnees(source_url="", page=3, nom_document=""),
            )
        ]
    )
    paragraphes = [
        Paragraphe(
            contenu="Source 1",
            url="https://exemple.fr/document.pdf",
            score_similarite=0.9,
            numero_page=3,
            nom_document="document.pdf",
            identifiant_document=4777455,
        ),
        Paragraphe(
            contenu="Source 2",
            url="https://exemple.fr/document.pdf",
            score_similarite=0.8,
            numero_page=3,
            nom_document="document.pdf",
            identifiant_document=4777455,
        ),
    ]

    ParPagePrecedenteEtSuivante(recuperateur).enrichis(paragraphes)

    assert recuperateur.identifiants_documents_recus == [4777455]
