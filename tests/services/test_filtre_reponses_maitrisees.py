from services.service_albert import filtre_reponses_maitrisees


def test_retourne_uniquement_les_chunks_maitrisees_si_score_combine_superieur_au_seuil(
    un_paragraphe_depuis_metadata,
):
    seuil = 0.8
    maitrise = un_paragraphe_depuis_metadata(
        contenu="Qui est le directeur de l'ANSSI ?",
        reponse_metadata="Vincent Strubel.",
        score_similarite=0.9,
        score_reclassement=0.95,
    )
    ordinaire = un_paragraphe_depuis_metadata(
        contenu="Autre contenu sans réponse",
        reponse_metadata="",
        score_similarite=0.8,
        score_reclassement=0.7,
    )

    resultat = filtre_reponses_maitrisees([maitrise, ordinaire], seuil)

    assert resultat == [maitrise]
