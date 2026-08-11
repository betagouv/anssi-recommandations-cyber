def test_contexte_dans_le_document_reste_le_texte_brut_pour_un_paragraphe_legacy(
    un_constructeur_de_paragraphe,
):
    paragraphe = (
        un_constructeur_de_paragraphe().avec_contenu("Un contenu sans métadonnée").construis()
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
        paragraphe.contexte_dans_le_document
        == "Question fréquente\nRéponse maîtrisée"
    )
