from client_albert_de_test import (
    ClientAlbertMemoire,
    un_resultat_de_recherche,
    un_choix_de_proposition,
)
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest
from schemas.albert import ReclasseReponse, ResultatReclasse
from serveur_de_test import AdaptateurExecuteurDeRequetesMemoire
from services.service_albert import ServiceAlbert, Prompts

PROMPTS = Prompts(
    prompt_systeme="Prompt système : {chunks}",
    prompt_reclassement="Prompt de reclassement : {QUESTION}",
)


def test_retourne_uniquement_le_paragraphe_maitrise(
    un_reclasseur, une_configuration_de_service_albert
):
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
        configuration_service_albert=une_configuration_de_service_albert(),
        client=client,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=ReformulateurDeQuestionDeTest(),
        mapping_reponses=MappingReponsesMaitrisees(
            {"question-maitrisee": "Une réponse."}
        ),
        reclasseur=un_reclasseur,
        executeur_de_requetes=AdaptateurExecuteurDeRequetesMemoire(),
    ).pose_question(question="Ma question ?")

    assert len(reponse.paragraphes) == 1
    assert reponse.paragraphes[0].contenu == "Question maîtrisée"


def test_retourne_uniquement_les_chunks_maitrisees_si_score_combine_superieur_au_seuil(
    un_reclasseur, une_configuration_de_service_albert
):
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
        configuration_service_albert=une_configuration_de_service_albert(),
        client=client,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=ReformulateurDeQuestionDeTest(),
        mapping_reponses=MappingReponsesMaitrisees(
            {"qui-est-le-directeur-de-lanssi": "Vincent Strubel."}
        ),
        reclasseur=un_reclasseur,
        executeur_de_requetes=AdaptateurExecuteurDeRequetesMemoire(),
    ).pose_question(question="Qui est le directeur de l'ANSSI ?")

    assert len(reponse.paragraphes) == 1
