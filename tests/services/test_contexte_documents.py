from schemas.albert import Paragraphe
from schemas.msc import DocumentGuideMSC, ReponseGuideMSC
from services.contexte_documents import associe_contexte_msc, texte_visible_description


def test_associe_uniquement_les_metadonnees_msc_au_nom_de_fichier_unique():
    guides = [
        ReponseGuideMSC(
            id="guide-un",
            nom="Guide exact",
            description="Description complète du guide exact.",
            listeDocuments=[
                DocumentGuideMSC(
                    libelle="Télécharger",
                    nomFichier="guide.pdf",
                )
            ],
            dateMiseAJour="2026-01-01",
        ),
        ReponseGuideMSC(
            id="guide-deux",
            nom="Guide ambigu",
            description="Description concurrente.",
            listeDocuments=[
                DocumentGuideMSC(
                    libelle="Télécharger",
                    nomFichier="ambigu.pdf",
                )
            ],
            dateMiseAJour="2026-01-02",
        ),
        ReponseGuideMSC(
            id="guide-trois",
            nom="Guide ambigu bis",
            description="Autre description concurrente.",
            listeDocuments=[
                DocumentGuideMSC(
                    libelle="Télécharger",
                    nomFichier="ambigu.pdf",
                )
            ],
            dateMiseAJour="2026-01-03",
        ),
    ]
    paragraphes = [
        Paragraphe(
            contenu="Texte.",
            url="https://exemple.test/guide.pdf",
            score_similarite=0.8,
            numero_page=1,
            nom_document="guide.pdf",
        ),
        Paragraphe(
            contenu="Texte.",
            url="https://exemple.test/ambigu.pdf",
            score_similarite=0.7,
            numero_page=2,
            nom_document="ambigu.pdf",
        ),
        Paragraphe(
            contenu="Texte.",
            url="https://exemple.test/inconnu.pdf",
            score_similarite=0.6,
            numero_page=3,
            nom_document="inconnu.pdf",
        ),
    ]

    associes = associe_contexte_msc(paragraphes, guides)

    assert associes[0].contexte_document_msc is not None
    assert associes[0].contexte_document_msc.nom == "Guide exact"
    assert (
        associes[0].contexte_document_msc.description
        == "Description complète du guide exact."
    )
    assert associes[1].contexte_document_msc is None
    assert associes[2].contexte_document_msc is None


def test_convertit_une_description_html_en_texte_visible_structure():
    description = "<p>Stockage <strong>chiffré</strong> &amp; protégé</p><ul><li>sel</li><li>paramètres</li></ul><script>secret</script>"

    assert (
        texte_visible_description(description)
        == "Stockage chiffré & protégé\n\n- sel\n- paramètres"
    )
