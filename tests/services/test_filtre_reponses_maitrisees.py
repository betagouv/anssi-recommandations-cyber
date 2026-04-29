from client_albert_de_test import (
    ClientAlbertMemoire,
    un_resultat_de_recherche,
    un_choix_de_proposition,
)
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest

from configuration import Albert
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from schemas.albert import ParagrapheReponseMaitrisee, ReclasseReponse, ResultatReclasse
from services.service_albert import ServiceAlbert, Prompts

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


def test_retourne_uniquement_le_paragraphe_maitrise():
    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu("Paragraphe sans réponse maîtrisée")
            .construis(),
            un_resultat_de_recherche()
            .ayant_pour_contenu("Question maîtrisée")
            .ayant_reponse_maitrisee("question-maitrisee")
            .construis(),
        ]
    )
    client.reclassement = ReclasseReponse(
        data=[
            ResultatReclasse(object="rerank", score=0.85, index=0),
            ResultatReclasse(object="rerank", score=0.9, index=1),
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
        mapping_reponses=MappingReponsesMaitrisees(
            {"question-maitrisee": "Une réponse."}
        ),
    ).pose_question(question="Ma question ?")

    assert len(reponse.paragraphes) == 1
    assert isinstance(reponse.paragraphes[0], ParagrapheReponseMaitrisee)


def test_retourne_uniquement_les_chunks_maitrisees_si_score_combine_superieur_au_seuil():
    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu("Qui est le directeur de l'ANSSI ?")
            .ayant_reponse_maitrisee("qui-est-le-directeur-de-lanssi")
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
        mapping_reponses=MappingReponsesMaitrisees(
            {"qui-est-le-directeur-de-lanssi": "Vincent Strubel."}
        ),
    ).pose_question(question="Qui est le directeur de l'ANSSI ?")

    assert len(reponse.paragraphes) == 1
