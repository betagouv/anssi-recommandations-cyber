import json

from client_albert_de_test import (
    ClientAlbertMemoire,
    un_choix_de_proposition,
    un_resultat_de_recherche,
)
from configuration import Albert, TypeReclasseur
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest
from schemas.violations import ViolationMeconnaissance
from services.reclasseur import ReclasseurBGE, ReclasseurLLM
from services.service_albert import Prompts, ServiceAlbert


PROMPTS = Prompts(
    prompt_systeme="Documents : {chunks}",
    prompt_reclassement=(
        "Question : {QUESTION}\n\nCandidats :\n{CANDIDATS}\n\nRetourne du JSON."
    ),
)


def une_configuration(
    type_reclasseur: TypeReclasseur, seuil_reponse_maitrisee: float = 0.5
) -> Albert.Service:  # type: ignore[name-defined, attr-defined]
    return Albert.Service(  # type: ignore[attr-defined]
        collection_nom_anssi_lab="",
        id_collection_anssi_lab=42,
        id_collection_anssi_lab_jeopardy=43,
        reclassement_active=True,
        modele_reclassement="bge-reranker-v2-m3",
        taille_fenetre_historique=2,
        jeopardy_active=False,
        seuil_reponse_maitrisee=seuil_reponse_maitrisee,
        nombre_paragraphes=1,
        type_reclasseur=type_reclasseur,
    )


def construit_service(
    client: ClientAlbertMemoire, type_reclasseur: TypeReclasseur
) -> ServiceAlbert:
    prompt_reclassement = (
        "Question BGE : {QUESTION}"
        if type_reclasseur is TypeReclasseur.BGE
        else PROMPTS.prompt_reclassement
    )
    return ServiceAlbert(
        configuration_service_albert=une_configuration(type_reclasseur),
        client=client,
        utilise_recherche_hybride=False,
        prompts=Prompts(
            prompt_systeme=PROMPTS.prompt_systeme,
            prompt_reclassement=prompt_reclassement,
        ),
        reformulateur=ReformulateurDeQuestionDeTest(),
        mapping_reponses=MappingReponsesMaitrisees({}),
    )


def test_selectionne_le_reclasseur_bge_par_configuration():
    service = construit_service(ClientAlbertMemoire(), TypeReclasseur.BGE)

    assert isinstance(service.reclasseur, ReclasseurBGE)
    assert service.reclasseur.prompt == "Question BGE : {QUESTION}"


def test_le_type_de_reclasseur_est_bge_par_defaut():
    configuration = Albert.Service(
        collection_nom_anssi_lab="",
        id_collection_anssi_lab=42,
        id_collection_anssi_lab_jeopardy=43,
        reclassement_active=True,
        modele_reclassement="bge-reranker-v2-m3",
        taille_fenetre_historique=2,
        jeopardy_active=False,
        seuil_reponse_maitrisee=0.5,
        nombre_paragraphes=1,
    )

    assert configuration.type_reclasseur is TypeReclasseur.BGE


def test_selectionne_le_reclasseur_llm_par_configuration():
    service = construit_service(ClientAlbertMemoire(), TypeReclasseur.LLM)

    assert isinstance(service.reclasseur, ReclasseurLLM)
    assert service.reclasseur.prompt == PROMPTS.prompt_reclassement


def test_reclasseur_llm_envoie_les_candidats_et_ne_conserve_que_les_preuves_principales(
    caplog,
):
    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu("Passage dans la thématique, sans réponse")
            .construis(),
            un_resultat_de_recherche()
            .ayant_pour_contenu("R50 Stocker les mots de passe dans un coffre-fort.")
            .construis(),
            un_resultat_de_recherche()
            .ayant_pour_contenu("Une recommandation complémentaire utile.")
            .construis(),
        ]
    )
    client.avec_les_propositions_par_appel(
        [
            [
                un_choix_de_proposition()
                .ayant_pour_contenu(
                    json.dumps(
                        {
                            "evaluations": [
                                {
                                    "id": 1,
                                    "categorie": "dans_la_thematique_sans_apport",
                                },
                                {"id": 2, "categorie": "preuve_principale"},
                                {"id": 3, "categorie": "element_de_reponse"},
                            ],
                            "ids_retenus": [3, 2],
                        }
                    )
                )
                .construis()
            ],
            [
                un_choix_de_proposition()
                .ayant_pour_contenu("Réponse finale")
                .construis()
            ],
        ]
    )

    reponse = construit_service(client, TypeReclasseur.LLM).pose_question(
        question="Quelles sont les recommandations sur les mots de passe ?"
    )

    assert [p.contenu for p in reponse.paragraphes] == [
        "R50 Stocker les mots de passe dans un coffre-fort."
    ]
    assert len(client.messages_recus_par_appel) == 2
    assert client.contextes_recus == ["reclassement_llm", "generation"]
    assert client.temperatures_recues == [0, None]
    assert "[PASSAGE id=1" in client.messages_recus_par_appel[0][0]["content"]
    assert "rang_initial=1" in client.messages_recus_par_appel[0][0]["content"]
    assert (
        "R50 Stocker les mots de passe dans un coffre-fort."
        in client.messages_recus_par_appel[0][0]["content"]
    )
    assert (
        "Passage dans la thématique, sans réponse"
        not in client.messages_recus_par_appel[1][0]["content"]
    )
    assert (
        "Une recommandation complémentaire utile."
        not in client.messages_recus_par_appel[1][0]["content"]
    )
    assert "[RECLASSEMENT_LLM] réponse JSON brute" in caplog.text
    assert '"ids_retenus": [3, 2]' in caplog.text


def test_reclasseur_llm_retourne_une_meconnaissance_sans_appeler_la_generation_si_aucun_passage_n_est_utile():
    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu("Une bibliographie.")
            .construis()
        ]
    )
    client.avec_les_propositions_par_appel(
        [
            [
                un_choix_de_proposition()
                .ayant_pour_contenu(
                    json.dumps(
                        {
                            "evaluations": [
                                {"id": 1, "categorie": "dans_la_thematique_sans_apport"}
                            ],
                            "ids_retenus": [],
                        }
                    )
                )
                .construis()
            ]
        ]
    )

    reponse = construit_service(client, TypeReclasseur.LLM).pose_question(
        question="Question ?"
    )

    assert reponse.violation == ViolationMeconnaissance()
    assert reponse.paragraphes == []
    assert len(client.messages_recus_par_appel) == 1


def test_reclasseur_llm_donne_priorite_a_une_reponse_maitrisee_retenue():
    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu("Réponse maîtrisée")
            .ayant_reponse_maitrisee("reponse-maitrisee")
            .construis(),
            un_resultat_de_recherche().ayant_pour_contenu("Autre preuve").construis(),
        ]
    )
    client.avec_les_propositions_par_appel(
        [
            [
                un_choix_de_proposition()
                .ayant_pour_contenu(
                    json.dumps(
                        {
                            "evaluations": [
                                {"id": 1, "categorie": "preuve_principale"},
                                {"id": 2, "categorie": "preuve_principale"},
                            ],
                            "ids_retenus": [2, 1],
                        }
                    )
                )
                .construis()
            ],
            [
                un_choix_de_proposition()
                .ayant_pour_contenu("Réponse finale")
                .construis()
            ],
        ]
    )
    service = ServiceAlbert(
        configuration_service_albert=une_configuration(TypeReclasseur.LLM),
        client=client,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=ReformulateurDeQuestionDeTest(),
        mapping_reponses=MappingReponsesMaitrisees(
            {"reponse-maitrisee": "La réponse maîtrisée complète."}
        ),
    )

    reponse = service.pose_question(question="Question ?")

    assert [p.contenu for p in reponse.paragraphes] == ["Réponse maîtrisée"]


def test_reclasseur_llm_ne_priorise_pas_une_reponse_maitrisee_sous_le_seuil():
    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu("Réponse maîtrisée")
            .ayant_reponse_maitrisee("reponse-maitrisee")
            .construis(),
            un_resultat_de_recherche().ayant_pour_contenu("Autre preuve").construis(),
        ]
    )
    client.avec_les_propositions_par_appel(
        [
            [
                un_choix_de_proposition()
                .ayant_pour_contenu(
                    json.dumps(
                        {
                            "evaluations": [
                                {"id": 1, "categorie": "preuve_principale"},
                                {"id": 2, "categorie": "preuve_principale"},
                            ],
                            "ids_retenus": [2, 1],
                        }
                    )
                )
                .construis()
            ],
            [
                un_choix_de_proposition()
                .ayant_pour_contenu("Réponse finale")
                .construis()
            ],
        ]
    )
    service = ServiceAlbert(
        configuration_service_albert=une_configuration(
            TypeReclasseur.LLM, seuil_reponse_maitrisee=1.1
        ),
        client=client,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=ReformulateurDeQuestionDeTest(),
        mapping_reponses=MappingReponsesMaitrisees(
            {"reponse-maitrisee": "La réponse maîtrisée complète."}
        ),
    )

    reponse = service.pose_question(question="Question ?")

    assert [p.contenu for p in reponse.paragraphes] == [
        "Autre preuve",
        "Réponse maîtrisée",
    ]
