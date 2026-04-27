from client_albert_de_test import (
    ClientAlbertMemoire,
    un_resultat_de_recherche,
    un_choix_de_proposition,
)
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest

from configuration import Albert
from schemas.albert import ReclasseReponse, ResultatReclasse
from services.service_albert import ServiceAlbert, Prompts, _filtre_reponses_maitrisees

PROMPTS = Prompts(
    prompt_systeme="Prompt système : {chunks}",
    prompt_reclassement="Prompt de reclassement : {QUESTION}",
)

FAUSSE_CONFIGURATION_AVEC_RECLASSEMENT_ET_SEUIL = Albert.Service(  # type: ignore [attr-defined]
    collection_nom_anssi_lab="",
    collection_id_anssi_lab=42,
    collection_id_anssi_lab_jeopardy=43,
    reclassement_active=True,
    modele_reclassement="rerank-small",
    taille_fenetre_historique=2,
    jeopardy_active=False,
    seuil_reponse_maitrisee=0.8,
)


def test_retourne_uniquement_le_paragraphe_maitrise(
    un_paragraphe_depuis_metadata,
):
    seuil = 0.8
    ordinaire = un_paragraphe_depuis_metadata(
        contenu="Paragraphe sans réponse maîtrisée",
        score_similarite=0.9,
        score_reclassement=0.95,
    )
    paragraphe_maitrise = un_paragraphe_depuis_metadata(
        contenu="Question maîtrisée sous le seuil",
        reponse_metadata="Une réponse.",
        score_similarite=0.9,
        score_reclassement=0.9,
    )

    resultat = _filtre_reponses_maitrisees([ordinaire, paragraphe_maitrise], seuil)

    assert resultat == [paragraphe_maitrise]


def test_retourne_uniquement_les_chunks_maitrisees_si_score_combine_superieur_au_seuil():
    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu("Qui est le directeur de l'ANSSI ?")
            .ayant_pour_reponse("Vincent Strubel.")
            .construis(),
            un_resultat_de_recherche()
            .ayant_pour_contenu("Autre contenu sans réponse")
            .construis(),
        ]
    )
    client.reclassement = ReclasseReponse(
        data=[
            ResultatReclasse(object="rerank", score=0.95, index=0),
            ResultatReclasse(object="rerank", score=0.7, index=1),
        ]
    )
    client.avec_les_propositions(
        [un_choix_de_proposition().ayant_pour_contenu("Réponse").construis()]
    )

    reponse = ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_AVEC_RECLASSEMENT_ET_SEUIL,
        client=client,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=ReformulateurDeQuestionDeTest(),
    ).pose_question(question="Qui est le directeur de l'ANSSI ?")

    assert len(reponse.paragraphes) == 1
    assert reponse.paragraphes[0].est_maitrisee is True
