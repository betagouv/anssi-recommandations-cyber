from typing import Any

from schemas.albert import (
    Paragraphe,
    RechercheChunk,
    RechercheMetadonnees,
    UniteSource,
)

URL = "https://example.com/guide.pdf"
METADONNEES: dict[str, Any] = {
    "type_de_bloc": "recommandation",
    "code_recommandation": "R42",
    "chemin_sections": ["1 Introduction", "1.2 Périmètre"],
}


def test_contexte_dans_le_document_reste_le_texte_brut_pour_un_paragraphe_legacy(
    un_constructeur_de_paragraphe,
):
    paragraphe = (
        un_constructeur_de_paragraphe()
        .avec_contenu("Un contenu sans métadonnée")
        .construis()
    )

    assert paragraphe.contexte_dans_le_document == "Un contenu sans métadonnée"


def test_contexte_dans_le_document_prefixe_un_en_tete_structure_si_metadonnees_presentes(
    un_constructeur_de_paragraphe,
):
    paragraphe = (
        un_constructeur_de_paragraphe()
        .avec_contenu("R3 Utiliser ESP plutôt que AH.")
        .dans_le_document("NT_IPsec.pdf")
        .ayant_pour_metadonnees_de_bloc(
            type_de_bloc="recommandation",
            code_recommandation="R3",
            chemin_sections=[
                "6 Fonctionnement d'IPsec",
                "6.1 Services fournis par IPsec",
                "6.1.1 AH",
            ],
        )
        .construis()
    )

    contexte = paragraphe.contexte_dans_le_document

    assert contexte.startswith(
        "[Document: NT_IPsec.pdf | Section: 6.1 Services fournis par IPsec > 6.1.1 AH | Recommandation: R3]\n"
    )
    assert contexte.endswith("R3 Utiliser ESP plutôt que AH.")


def test_contexte_dans_le_document_omet_la_recommandation_si_absente(
    un_constructeur_de_paragraphe,
):
    paragraphe = (
        un_constructeur_de_paragraphe()
        .avec_contenu("Contenu explicatif.")
        .dans_le_document("NT_IPsec.pdf")
        .ayant_pour_metadonnees_de_bloc(
            type_de_bloc="paragraphe",
            chemin_sections=["6 Fonctionnement d'IPsec"],
        )
        .construis()
    )

    contexte = paragraphe.contexte_dans_le_document

    assert (
        contexte
        == "[Document: NT_IPsec.pdf | Section: 6 Fonctionnement d'IPsec]\nContenu explicatif."
    )


def test_contexte_dans_le_document_de_reponse_maitrisee_conserve_la_reponse_associee(
    un_constructeur_de_paragraphe_reponse_maitrisee,
):
    paragraphe = (
        un_constructeur_de_paragraphe_reponse_maitrisee()
        .avec_contenu("Question fréquente")
        .construis()
    )
    paragraphe = paragraphe.model_copy(update={"reponse": "Réponse maîtrisée"})

    assert (
        paragraphe.contexte_dans_le_document == "Question fréquente\nRéponse maîtrisée"
    )


def test_une_unite_source_depuis_un_chunk_reprend_son_contenu_et_ses_metadonnees():
    metadonnees = RechercheMetadonnees(
        source_url=URL, page=12, nom_document="Guide", **METADONNEES
    )
    chunk = RechercheChunk(content="Contenu du chunk", metadata=metadonnees)

    assert UniteSource.depuis_chunk(chunk) == UniteSource(
        contenu="Contenu du chunk", url=URL, numero_page=12, **METADONNEES
    )


def test_une_unite_source_depuis_un_paragraphe_reprend_ses_metadonnees():
    paragraphe = Paragraphe(
        score_similarite=0.8,
        contenu="Contenu complet",
        url=URL,
        numero_page=12,
        nom_document="Guide",
        **METADONNEES,
    )

    assert UniteSource.depuis_paragraphe(paragraphe, "Un extrait") == UniteSource(
        contenu="Un extrait", url=URL, numero_page=12, **METADONNEES
    )
