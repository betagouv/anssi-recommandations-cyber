import pytest

from schemas.msc import DocumentGuideMSC, ReponseGuideMSC
from services.contexte_documents import associe_contexte_msc, texte_visible_description


def un_guide(nom: str, description: str, *noms_fichiers: str) -> ReponseGuideMSC:
    return ReponseGuideMSC(
        id=nom,
        nom=nom,
        description=description,
        listeDocuments=[
            DocumentGuideMSC(libelle="Télécharger", nomFichier=fichier)
            for fichier in noms_fichiers
        ],
        dateMiseAJour="2026-01-01",
    )


def test_associe_le_contexte_d_un_guide_unique_et_ignore_les_documents_ambigus(
    un_constructeur_de_paragraphe,
) -> None:
    guides = [
        un_guide("Guide exact", "<p>Description</p>", "exact.pdf"),
        un_guide("Guide ambigu", "Concurrent", "ambigu.pdf"),
        un_guide("Guide ambigu bis", "Concurrent bis", "ambigu.pdf"),
    ]
    paragraphes = [
        un_constructeur_de_paragraphe().dans_le_document(document).construis()
        for document in ("exact.pdf", "ambigu.pdf", "inconnu.pdf")
    ]

    exact, ambigu, inconnu = associe_contexte_msc(paragraphes, guides)

    assert exact.contexte_document_msc is not None
    assert exact.contexte_document_msc.nom == "Guide exact"
    assert exact.contexte_document_msc.description == "Description"
    assert ambigu.contexte_document_msc is None
    assert inconnu.contexte_document_msc is None


@pytest.mark.parametrize(
    ("description", "texte"),
    [
        (
            "<p>Stockage <strong>chiffré</strong> &amp; protégé</p>",
            "Stockage chiffré & protégé",
        ),
        ("<ul><li>sel</li><li>paramètres</li></ul>", "sel paramètres"),
        ("Avant<script>secret()</script> après", "Avant après"),
    ],
)
def test_ne_garde_que_le_texte_visible_d_une_description_html(description, texte):
    assert texte_visible_description(description) == texte
