import json
import pytest

from client_albert_de_test import (
    ClientAlbertMemoire,
    un_resultat_de_recherche,
    un_choix_de_proposition,
    un_constructeur_de_reponse_de_reclassement,
)
from client_albert_de_test import ConstructeurDeChoix
from configuration import TypeReclasseur
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from schemas.albert import (
    Paragraphe,
    ParagrapheReponseMaitrisee,
)
from schemas.msc import DocumentGuideMSC, ReponseGuideMSC
from schemas.violations import (
    REPONSE_PAR_DEFAUT,
    Violation,
    ViolationIdentite,
    ViolationMalveillance,
    ViolationThematique,
    ViolationQuestionNonComprise,
    ViolationMeconnaissance,
)
from adaptateurs.bus_evenements import BusEvenementsEnMemoire, ErreurTechniqueSurvenue
from services.exceptions import ErreurCommunicationModeleGeneration
from services.reclasseur import (
    ReclasseurLLM,
    ResultatReclassement,
)
from reclassement_parallele_support import (
    classification_element_de_reponse,
    classification_preuve_principale,
    configure_reponses_par_appel,
    cree_reclasseur_llm_en_parallele,
    reponse_classification_avec_identifiants_globaux,
)


def test_mapping_historique_propage_une_erreur_de_recuperation_msc(
    une_configuration_de_service_albert, un_service_albert_de_test
):
    class ExecuteurMscIndisponible:
        def recupere(self, url, schema):
            raise RuntimeError("indisponible")

    client = ClientAlbertMemoire()
    service = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client,
        reclasseur=ReclasseurLLM(client, "", BusEvenementsEnMemoire()),
        executeur_de_requetes=ExecuteurMscIndisponible(),
    )
    paragraphe = Paragraphe(
        score_similarite=0.9,
        numero_page=1,
        url="https://exemple.invalid/source",
        nom_document="source.pdf",
        contenu="Contenu source.",
    )

    with pytest.raises(RuntimeError, match="indisponible"):
        service._mappe_en_paragraphes_pour_la_reponse([paragraphe])


def test_mapping_historique_garde_le_premier_guide_pour_un_nom_de_fichier_duplique(
    une_configuration_de_service_albert, un_service_albert_de_test
):
    class ExecuteurMsc:
        def recupere(self, url, schema):
            return [
                ReponseGuideMSC(
                    id="premier",
                    nom="Premier guide",
                    description="Premier résultat historique.",
                    listeDocuments=[
                        DocumentGuideMSC(libelle="A", nomFichier="source.pdf")
                    ],
                    dateMiseAJour="2026-01-01",
                ),
                ReponseGuideMSC(
                    id="second",
                    nom="Second guide",
                    description="Second résultat.",
                    listeDocuments=[
                        DocumentGuideMSC(libelle="B", nomFichier="source.pdf")
                    ],
                    dateMiseAJour="2026-02-01",
                ),
            ]

    client = ClientAlbertMemoire()
    service = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client,
        reclasseur=ReclasseurLLM(client, "", BusEvenementsEnMemoire()),
        executeur_de_requetes=ExecuteurMsc(),
    )
    paragraphe = Paragraphe(
        score_similarite=0.9,
        numero_page=1,
        url="https://exemple.invalid/source",
        nom_document="source.pdf",
        contenu="Contenu source.",
    )

    mapped = service._mappe_en_paragraphes_pour_la_reponse([paragraphe])

    assert mapped[0].titre == "Premier guide"
    assert mapped[0].date_mise_a_jour == "2026-01-01"


QUESTION = "Quelle est la recette de la tartiflette ?"
REPONSE = "Patates et reblochon"
FAUX_CONTENU = "La tartiflette est une recette de cuisine à base de gratin de pommes de terre, d'oignons et de lardons, le tout gratiné au reblochon."


def test_pose_question_leve_une_erreur_de_generation_si_la_communication_avec_le_modele_echoue(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_resultats(
        [un_resultat_de_recherche().ayant_pour_contenu(REPONSE).construis()]
    )
    client_albert_memoire.qui_leve_une_erreur_de_communication_modele()
    service_albert = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    )

    with pytest.raises(ErreurCommunicationModeleGeneration):
        service_albert.pose_question(question=QUESTION)


def test_pose_question_publie_une_erreur_technique_sur_le_bus_si_la_generation_echoue(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
    bus = BusEvenementsEnMemoire()
    erreurs_publiees: list[ErreurTechniqueSurvenue] = []
    bus.souscris(ErreurTechniqueSurvenue, erreurs_publiees.append)
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_resultats(
        [un_resultat_de_recherche().ayant_pour_contenu(REPONSE).construis()]
    )
    client_albert_memoire.qui_leve_une_erreur_de_communication_modele()
    service_albert = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
        bus_evenements=bus,
    )

    with pytest.raises(ErreurCommunicationModeleGeneration):
        service_albert.pose_question(question=QUESTION)

    assert len(erreurs_publiees) == 1
    assert isinstance(
        erreurs_publiees[0].exception, ErreurCommunicationModeleGeneration
    )


def test_pose_question_retourne_une_reponse(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_resultats(
        [
            un_resultat_de_recherche().ayant_pour_contenu(REPONSE).construis(),
        ]
    )
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )
    service_albert = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reformulateur=un_reformulateur_albert_de_test(client_albert_memoire),
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    )

    reponse = service_albert.pose_question(question=QUESTION)

    assert reponse.reponse == REPONSE
    assert len(reponse.paragraphes) == 1
    assert reponse.question == QUESTION
    assert reponse.violation is None


def test_recherche_paragraphes_propage_les_nouvelles_metadonnees_de_chunk(
    un_reclasseur,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu(REPONSE)
            .ayant_pour_metadonnees_de_bloc(
                type_de_bloc="recommandation",
                code_recommandation="R3",
                chemin_sections=["6 Fonctionnement", "6.1 Services"],
            )
            .construis(),
        ]
    )
    service_albert = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reformulateur=un_reformulateur_albert_de_test(client_albert_memoire),
        reclasseur=un_reclasseur,
        executeur_de_requetes=None,
    )

    paragraphes = service_albert.recherche_paragraphes(QUESTION)

    assert paragraphes[0].type_de_bloc == "recommandation"
    assert paragraphes[0].code_recommandation == "R3"
    assert paragraphes[0].chemin_sections == ["6 Fonctionnement", "6.1 Services"]


def test_recherche_paragraphes_utilise_des_metadonnees_par_defaut_pour_un_chunk_legacy(
    un_reclasseur,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_resultats(
        [
            un_resultat_de_recherche().ayant_pour_contenu(REPONSE).construis(),
        ]
    )
    service_albert = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reformulateur=un_reformulateur_albert_de_test(client_albert_memoire),
        reclasseur=un_reclasseur,
        executeur_de_requetes=None,
    )

    paragraphes = service_albert.recherche_paragraphes(QUESTION)

    assert paragraphes[0].type_de_bloc is None
    assert paragraphes[0].code_recommandation is None
    assert paragraphes[0].chemin_sections == []


def test_reclasseur_parallele_charge_msc_avant_classement_et_reutilise_le_resultat(
    une_configuration_de_service_albert, un_service_albert_de_test
):
    evenements = []
    nom_document = "authentification.pdf"

    class ExecuteurMsc:
        def __init__(self):
            self.appels = 0

        def recupere(self, url, schema):
            self.appels += 1
            evenements.append("msc")
            assert url.endswith("/api/guides")
            return [
                ReponseGuideMSC(
                    id="guide-mots-de-passe",
                    nom="Guide des mots de passe",
                    description="Stockage et vérification des mots de passe.",
                    listeDocuments=[
                        DocumentGuideMSC(
                            libelle="Authentification", nomFichier=nom_document
                        )
                    ],
                    dateMiseAJour="2026-01-01",
                )
            ]

    class ReclasseurAvecContexteMsc:
        requiert_contexte_documents_msc = True

        def reclasse(self, question, paragraphes):
            evenements.append(("classement", paragraphes[0].contexte_document_msc))
            return ResultatReclassement(paragraphes, paragraphes)

    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu("Utiliser un mécanisme de stockage sécurisé.")
            .ayant_pour_document(nom_document)
            .construis()
        ]
    )
    client.avec_les_propositions(
        [un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis()]
    )
    executeur_msc = ExecuteurMsc()
    service = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client,
        reclasseur=ReclasseurAvecContexteMsc(),
        executeur_de_requetes=executeur_msc,
    )

    reponse = service.pose_question(question=QUESTION)

    assert executeur_msc.appels == 1
    assert evenements[0] == "msc"
    assert evenements[1][0] == "classement"
    assert evenements[1][1].nom == "Guide des mots de passe"
    assert reponse.paragraphes[0].titre == "Guide des mots de passe"


def test_echec_msc_est_reutilise_comme_contexte_inconnu_sans_second_get(
    une_configuration_de_service_albert, un_service_albert_de_test
):
    class ExecuteurMscIndisponible:
        appels = 0

        def recupere(self, url, schema):
            self.appels += 1
            raise RuntimeError("MSC indisponible")

    class ReclasseurSansContexteMsc:
        requiert_contexte_documents_msc = True
        contexte_observe = "non consulté"

        def reclasse(self, question, paragraphes):
            self.contexte_observe = paragraphes[0].contexte_document_msc
            return ResultatReclassement(paragraphes, paragraphes)

    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [un_resultat_de_recherche().ayant_pour_contenu(REPONSE).construis()]
    )
    client.avec_les_propositions(
        [un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis()]
    )
    executeur = ExecuteurMscIndisponible()
    reclasseur = ReclasseurSansContexteMsc()
    service = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client,
        reclasseur=reclasseur,
        executeur_de_requetes=executeur,
    )

    reponse = service.pose_question(question=QUESTION)

    assert executeur.appels == 1
    assert reclasseur.contexte_observe is None
    assert reponse.paragraphes[0].titre == ""


def test_ne_genere_pas_de_reponse_si_aucune_preuve_directe_n_est_eligible(
    une_configuration_de_service_albert, un_service_albert_de_test
):
    class ReclasseurSansPreuveEligible:
        def reclasse(self, question, paragraphes):
            return ResultatReclassement([], paragraphes, aucune_source_utile=True)

    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [un_resultat_de_recherche().ayant_pour_contenu(REPONSE).construis()]
    )
    service = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client,
        reclasseur=ReclasseurSansPreuveEligible(),
        executeur_de_requetes=None,
    )

    reponse = service.pose_question(question=QUESTION)

    assert isinstance(reponse.violation, ViolationMeconnaissance)
    assert client.messages_envoyes_pour_les_propositions == []


def test_le_reclassement_parallele_transmet_une_preuve_a_la_generation(
    un_coordinateur_reclassement,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu("La source établit la mesure demandée.")
            .construis()
        ]
    )
    configure_reponses_par_appel(
        client,
        [
            reponse_classification_avec_identifiants_globaux(
                {1: classification_preuve_principale()}
            ),
            REPONSE,
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(client, un_coordinateur_reclassement)
    service = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client,
        reclasseur=reclasseur,
        executeur_de_requetes=None,
    )

    reponse = service.pose_question(question=QUESTION)

    assert reponse.reponse == REPONSE
    assert reponse.paragraphes[0].contenu == "La source établit la mesure demandée."
    assert sorted(client.noms_schemas_propositions[:2]) == [
        "classification_passages",
        "qualification_guides",
    ]
    assert client.noms_schemas_propositions[2] is None


def test_le_reclassement_parallele_emet_une_meconnaissance_sans_preuve_eligible(
    un_coordinateur_reclassement,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [un_resultat_de_recherche().ayant_pour_contenu("Passage indirect.").construis()]
    )
    configure_reponses_par_appel(
        client,
        [
            reponse_classification_avec_identifiants_globaux(
                {1: classification_element_de_reponse(relation="indirecte")}
            ),
            json.dumps({"D1": "consacre_au_sujet"}),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(client, un_coordinateur_reclassement)
    service = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client,
        reclasseur=reclasseur,
        executeur_de_requetes=None,
    )

    reponse = service.pose_question(question=QUESTION)

    assert isinstance(reponse.violation, ViolationMeconnaissance)
    assert sorted(client.noms_schemas_propositions) == [
        "classification_passages",
        "qualification_guides",
    ]


def test_pose_question_recupere_les_details_du_document_depuis_MSC(
    un_reclasseur,
    un_constructeur_d_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_document("un_titre.pdf")
            .ayant_pour_contenu(REPONSE)
            .construis(),
        ]
    )
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )
    executeur_de_requetes = un_constructeur_d_executeur_de_requetes.avec_comme_reponse(
        [
            {
                "id": "un-autre-id",
                "nom": "Un Nom",
                "description": "description",
                "listeDocuments": [
                    {
                        "libelle": "Télécharger le guide",
                        "nomFichier": "un_autre_titre.pdf",
                    }
                ],
                "dateMiseAJour": "2026-07-21T00:00:00.000Z",
            },
            {
                "id": "un-id",
                "nom": "Un Nom",
                "description": "description",
                "listeDocuments": [
                    {"libelle": "Télécharger le guide", "nomFichier": "un_titre.pdf"}
                ],
                "dateMiseAJour": "2026-06-15T10:00:00:000Z",
            },
        ]
    ).construis()
    service_albert = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reclasseur=un_reclasseur,
        executeur_de_requetes=executeur_de_requetes,
    )

    reponse = service_albert.pose_question(question=QUESTION)

    assert reponse.paragraphes[0].titre == "Un Nom"
    assert reponse.paragraphes[0].date_mise_a_jour == "2026-06-15T10:00:00:000Z"


def test_pose_question_retourne_une_reponse_generique_et_pas_de_violation_si_albert_ne_retourne_rien(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.sans_resultats()
    client_albert_memoire.sans_propositions()
    service_albert = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    )

    retour = service_albert.pose_question(question=QUESTION)

    assert retour.reponse == REPONSE_PAR_DEFAUT
    assert retour.paragraphes == []
    assert retour.violation is None


@pytest.mark.parametrize(
    "erreur,violation_attendue",
    [
        pytest.param(
            "ERREUR_MALVEILLANCE",
            ViolationMalveillance(),
            id="si_question_malveillante_retourne_message_malveillant_avec_paragraphes_vides",
        ),
        pytest.param(
            "ERREUR_THÉMATIQUE",
            ViolationThematique(),
            id="si_question_mauvaise_thematique_retourne_message_thematique_avec_paragraphes_vides",
        ),
        pytest.param(
            "ERREUR_IDENTITÉ",
            ViolationIdentite(),
            id="si_question_identite_retourne_message_identite_avec_paragraphes_vides",
        ),
    ],
)
def test_pose_question_illegale(
    erreur: str,
    violation_attendue: Violation,
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_resultats(
        [
            un_resultat_de_recherche().ayant_pour_contenu("Un contenu").construis(),
        ]
    )
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(erreur).construis(),
        ]
    )
    service_albert = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reformulateur=un_reformulateur_albert_de_test(client_albert_memoire),
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    )

    retour = service_albert.pose_question(question="question illégale ?")

    assert retour.reponse == violation_attendue.reponse
    assert retour.paragraphes == []
    assert retour.violation == violation_attendue


def test_le_score_reclassement_est_propage_sur_le_paragraphe(
    un_constructeur_de_reclasseur,
    un_constructeur_de_paragraphe,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    reponse = (
        un_constructeur_de_reponse_de_reclassement()
        .avec_les_paragraphes_les_mieux_classes(
            [
                {"titre": "paragraphe 1", "indice": 1, "score": 0.92},
            ]
        )
        .construis()
    )
    reclasseur = (
        un_constructeur_de_reclasseur()
        .avec_les_paragraphes(
            [un_constructeur_de_paragraphe().ayant_comme_score(0.92).construis()]
        )
        .construis()
    )
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_le_reclassement(reponse)
    client_albert_memoire.avec_les_propositions(
        [un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis()]
    )

    reponse_de_pose_question = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reformulateur=un_reformulateur_albert_de_test(client_albert_memoire),
        reclasseur=reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Une question ?")

    assert reponse_de_pose_question.paragraphes[0].score_reclassement == 0.92


def test_en_cas_de_reclassement_recherche_paragraphes_retourne_les_5_paragraphes_les_mieux_classes_parmi_les_20_retournes(
    un_constructeur_de_reclasseur,
    un_constructeur_de_paragraphe,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    reclasseur = (
        un_constructeur_de_reclasseur()
        .avec_les_paragraphes(
            [
                un_constructeur_de_paragraphe()
                .avec_contenu("paragraphe 1")
                .ayant_comme_score(0.9)
                .construis(),
                un_constructeur_de_paragraphe()
                .avec_contenu("paragraphe 4")
                .ayant_comme_score(0.8)
                .construis(),
                un_constructeur_de_paragraphe()
                .avec_contenu("paragraphe 7")
                .ayant_comme_score(0.7)
                .construis(),
                un_constructeur_de_paragraphe()
                .avec_contenu("paragraphe 19")
                .ayant_comme_score(0.66)
                .construis(),
                un_constructeur_de_paragraphe()
                .avec_contenu("paragraphe 3")
                .ayant_comme_score(0.63)
                .construis(),
            ]
        )
        .construis()
    )
    reponse = (
        un_constructeur_de_reponse_de_reclassement()
        .avec_les_paragraphes_les_mieux_classes(
            [
                {"titre": "paragraphe 1", "indice": 1, "score": 0.9},
                {"titre": "paragraphe 4", "indice": 4, "score": 0.8},
                {"titre": "paragraphe 7", "indice": 7, "score": 0.7},
                {"titre": "paragraphe 19", "indice": 19, "score": 0.66},
                {"titre": "paragraphe 3", "indice": 3, "score": 0.63},
            ]
        )
        .construis()
    )
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_le_reclassement(reponse)
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )

    reponse_de_pose_question = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reformulateur=un_reformulateur_albert_de_test(client_albert_memoire),
        reclasseur=reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Une question de test ?")

    assert list(map(lambda p: p.contenu, reponse_de_pose_question.paragraphes)) == [
        "paragraphe 1",
        "paragraphe 4",
        "paragraphe 7",
        "paragraphe 19",
        "paragraphe 3",
    ]


def test_retourne_20_paragraphes_en_effectuant_le_reclassement(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    reponse = un_constructeur_de_reponse_de_reclassement().construis()
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_le_reclassement(reponse)
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )

    un_service_albert_de_test(
        une_configuration_de_service_albert(nombre_paragraphes=20),
        client_albert_memoire,
        reformulateur=un_reformulateur_albert_de_test(client_albert_memoire),
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Une question de test ?")

    # Sans jeopardy mais avec reclassement, on demande 20 paragraphes classiques
    assert client_albert_memoire.payload_recu.limit == 20


def test_appelle_le_reclassement_uniquement_quand_active(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )

    un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reformulateur=un_reformulateur_albert_de_test(client_albert_memoire),
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Une question de test ?")

    assert client_albert_memoire.payload_reclassement_recu is None


def test_ne_reclasse_pas_si_la_recherche_de_paragraphes_retourne_un_resultat_vide(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.sans_resultats()

    reponse = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Une question de test ?")

    assert client_albert_memoire.payload_reclassement_recu is None
    assert reponse.reponse == REPONSE_PAR_DEFAUT


def test_retourne_les_resultats_de_recherche_si_le_reclassement_ne_retourne_pas_de_donnees(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.reclassement_vide()
    client_albert_memoire.avec_les_resultats(
        [
            un_resultat_de_recherche().ayant_pour_contenu("Un contenu").construis(),
        ]
    )
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu("Un contenu").construis(),
        ]
    )

    reponse = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reformulateur=un_reformulateur_albert_de_test(client_albert_memoire),
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Une question de test ?")

    assert reponse.reponse == "Un contenu"
    assert len(reponse.paragraphes) == 1
    assert reponse.question == "Une question de test ?"


def test_initie_une_conversation(
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    interaction = (
        un_constructeur_d_interaction()
        .avec_question("Une question de test ?")
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation()
        .avec_interaction(interaction=interaction)
        .ajoute_interaction(
            un_constructeur_d_interaction()
            .avec_question("Une deuxième question de test ?")
            .construis()
        )
        .construis()
    )

    un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_memoire,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(
        question="Une troisieme question de test ?", conversation=conversation
    )

    messages_recus = [
        message
        for message in client_albert_memoire.messages_recus
        if message["role"] != "system"
    ]
    assert [message["role"] for message in messages_recus] == [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
    ]


def test_limite_l_historique_a_2_interactions_passees(
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    conversation = un_constructeur_de_conversation().construis()
    for i in range(2, 7):
        conversation.ajoute_interaction(
            un_constructeur_d_interaction().avec_question(f"Question {i} ?").construis()
        )
    configuration_avec_fenetre_limitee = une_configuration_de_service_albert(
        taille_fenetre_historique=2
    )

    un_service_albert_de_test(
        configuration_avec_fenetre_limitee,
        client_albert_memoire,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Question actuelle ?", conversation=conversation)

    messages_recus = [
        message
        for message in client_albert_memoire.messages_recus
        if message["role"] != "system"
    ]
    assert [message["role"] for message in messages_recus] == [
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
    ]


def test_peut_reformuler_une_question(
    une_configuration_de_service_albert,
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    reformulateur = un_reformulateur_albert_de_test(
        client_albert_memoire, prompt="Mon prompt", modele="albert-small"
    )
    mon_choix = (
        ConstructeurDeChoix().ayant_pour_contenu("Ma question reformulee").construis()
    )
    client_albert_memoire.avec_les_propositions([mon_choix])

    reponse_question = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        ClientAlbertMemoire(),
        reformulateur=reformulateur,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Question actuelle ?", conversation=None)

    assert reponse_question.question_reformulee == "Ma question reformulee"


def test_recherche_paragraphes_utilise_la_question_reformulee(
    une_configuration_de_service_albert,
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    client_albert_recherche = ClientAlbertMemoire()
    client_albert_reformulation = ClientAlbertMemoire()
    reformulateur = un_reformulateur_albert_de_test(
        client_albert_reformulation, prompt="Mon prompt", modele="albert-small"
    )
    choix_reformulation = (
        ConstructeurDeChoix()
        .ayant_pour_contenu("Question reformulee pour recherche")
        .construis()
    )
    client_albert_reformulation.avec_les_propositions([choix_reformulation])

    un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_recherche,
        reformulateur=reformulateur,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Ma question brute ?")

    assert (
        client_albert_recherche.payload_recu.query
        == "Question reformulee pour recherche"
    )


def test_reclassement_utilise_la_question_reformulee(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    reponse = un_constructeur_de_reponse_de_reclassement().construis()
    client_albert_recherche = ClientAlbertMemoire()
    client_albert_reformulation = ClientAlbertMemoire()
    client_albert_recherche.avec_le_reclassement(reponse)
    client_albert_recherche.avec_les_propositions(
        [un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis()]
    )
    reformulateur = un_reformulateur_albert_de_test(
        client_albert_reformulation, prompt="Mon prompt", modele="albert-small"
    )
    choix_reformulation = (
        ConstructeurDeChoix()
        .ayant_pour_contenu("Question reformulee pour reclassement")
        .construis()
    )
    client_albert_reformulation.avec_les_propositions([choix_reformulation])

    un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_recherche,
        reformulateur=reformulateur,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Ma question brute ?")

    assert un_reclasseur.question_recue == "Question reformulee pour reclassement"


def test_pose_question_passe_la_conversation_au_reformulateur(
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    interaction = (
        un_constructeur_d_interaction()
        .avec_question("Qu'est-ce que le défacement ?")
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation().avec_interaction(interaction).construis()
    )

    client_albert_recherche = ClientAlbertMemoire()
    client_albert_reformulation = ClientAlbertMemoire()
    reformulateur = un_reformulateur_albert_de_test(
        client_albert_reformulation, prompt="Mon prompt", modele="albert-small"
    )
    choix_reformulation = (
        ConstructeurDeChoix()
        .ayant_pour_contenu("Question reformulee avec contexte")
        .construis()
    )
    client_albert_reformulation.avec_les_propositions([choix_reformulation])

    un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_recherche,
        reformulateur=reformulateur,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Comment s'en protéger ?", conversation=conversation)

    roles_recus = [
        message["role"]
        for message in client_albert_reformulation.messages_recus
        if message["role"] != "system"
    ]
    assert roles_recus == ["user", "assistant", "user"]


def test_recuperation_propositions_utilise_la_question_reformulee(
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    interaction = (
        un_constructeur_d_interaction()
        .avec_question("Question brute historique")
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation().avec_interaction(interaction).construis()
    )

    client_albert_recherche = ClientAlbertMemoire()
    client_albert_reformulation = ClientAlbertMemoire()
    reformulateur = un_reformulateur_albert_de_test(
        client_albert_reformulation, prompt="Mon prompt", modele="albert-small"
    )
    choix_reformulation = (
        ConstructeurDeChoix()
        .ayant_pour_contenu("Question actuelle reformulee")
        .construis()
    )
    client_albert_reformulation.avec_les_propositions([choix_reformulation])
    client_albert_recherche.avec_les_propositions(
        [un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis()]
    )

    un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_recherche,
        reformulateur=reformulateur,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Question actuelle brute", conversation=conversation)

    roles_recus = [
        message["role"]
        for message in client_albert_recherche.messages_recus
        if message["role"] != "system"
    ]
    assert roles_recus == ["user", "assistant", "user"]


def test_pose_question_reformule_la_question_sans_les_violations_precedentes(
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    interaction_sans_violation = (
        un_constructeur_d_interaction().avec_question("Question valide ?").construis()
    )
    interaction_avec_violation = (
        un_constructeur_d_interaction()
        .avec_question("Qui es-tu ?")
        .avec_une_violation(ViolationIdentite())
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation()
        .avec_interaction(interaction_sans_violation)
        .ajoute_interaction(interaction_avec_violation)
        .construis()
    )

    client_albert_reformulation = ClientAlbertMemoire()
    reformulateur = un_reformulateur_albert_de_test(
        client_albert_reformulation, prompt="Mon prompt", modele="albert-small"
    )
    choix_reformulation = (
        ConstructeurDeChoix().ayant_pour_contenu("Question reformulee").construis()
    )
    client_albert_reformulation.avec_les_propositions([choix_reformulation])

    un_service_albert_de_test(
        une_configuration_de_service_albert(),
        ClientAlbertMemoire(),
        reformulateur=reformulateur,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Nouvelle question ?", conversation=conversation)

    messages_reformulation = [
        message
        for message in client_albert_reformulation.messages_recus
        if message["role"] != "system"
    ]
    assert [message["role"] for message in messages_reformulation] == [
        "user",
        "assistant",
        "user",
    ]


def test_pose_question_recherche_les_paragraphes_sans_les_violations_precedentes(
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    interaction_sans_violation = (
        un_constructeur_d_interaction().avec_question("Question valide ?").construis()
    )
    interaction_avec_violation = (
        un_constructeur_d_interaction()
        .avec_question("Qui es-tu ?")
        .avec_une_violation(ViolationIdentite())
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation()
        .avec_interaction(interaction_sans_violation)
        .ajoute_interaction(interaction_avec_violation)
        .construis()
    )

    client_albert_recherche = ClientAlbertMemoire()
    client_albert_reformulation = ClientAlbertMemoire()
    reformulateur = un_reformulateur_albert_de_test(
        client_albert_reformulation, prompt="Mon prompt", modele="albert-small"
    )
    choix_reformulation = (
        ConstructeurDeChoix().ayant_pour_contenu("Question reformulee").construis()
    )
    client_albert_reformulation.avec_les_propositions([choix_reformulation])
    client_albert_recherche.avec_les_propositions(
        [un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis()]
    )

    un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_recherche,
        reformulateur=reformulateur,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Nouvelle question ?", conversation=conversation)

    messages_recherche = [
        message
        for message in client_albert_recherche.messages_recus
        if message["role"] != "system"
    ]
    assert [message["role"] for message in messages_recherche] == [
        "user",
        "assistant",
        "user",
    ]


def test_retourne_violation_question_non_comprise_si_reformulateur_retourne_QUESTION_NON_COMPRISE(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    client_albert_recherche = ClientAlbertMemoire()
    client_albert_reformulation = ClientAlbertMemoire()
    reformulateur = un_reformulateur_albert_de_test(
        client_albert_reformulation, prompt="Mon prompt", modele="albert-small"
    )
    choix_reformulation = (
        ConstructeurDeChoix().ayant_pour_contenu("QUESTION_NON_COMPRISE").construis()
    )
    client_albert_reformulation.avec_les_propositions([choix_reformulation])

    reponse = un_service_albert_de_test(
        une_configuration_de_service_albert(),
        client_albert_recherche,
        reformulateur=reformulateur,
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    ).pose_question(question="Raconte-moi une blague")

    assert reponse.violation == ViolationQuestionNonComprise()
    assert reponse.reponse == ViolationQuestionNonComprise().reponse
    assert reponse.paragraphes == []
    assert client_albert_recherche.payload_recu is None


def test_recherche_paragraphes_retourne_un_paragraphe_de_reponse_maitrisee(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
    un_reformulateur_albert_de_test,
):
    client_albert_memoire = ClientAlbertMemoire()
    resultats_classiques = [
        un_resultat_de_recherche()
        .ayant_reponse_maitrisee("quel-est-le-directeur-de-anssi")
        .ayant_pour_contenu("Quel est le directeur de l'ANSSI ?")
        .construis()
    ]
    client_albert_memoire.avec_les_resultats_par_appel([resultats_classiques])
    configuration = une_configuration_de_service_albert()

    service_albert = un_service_albert_de_test(
        configuration,
        client_albert_memoire,
        reformulateur=un_reformulateur_albert_de_test(client_albert_memoire),
        mapping_reponses=MappingReponsesMaitrisees(
            {"quel-est-le-directeur-de-anssi": "Vincent Strubel"}
        ),
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    )

    paragraphes = service_albert.recherche_paragraphes("Ma question ?")

    paragraphe_attendu = ParagrapheReponseMaitrisee(
        contenu="Quel est le directeur de l'ANSSI ?",
        url="",
        score_similarite=0.5,
        numero_page=1,
        nom_document="",
        reponse="Vincent Strubel",
        rang_initial=1,
    )
    assert paragraphes[0] == paragraphe_attendu
    assert (
        paragraphe_attendu.contexte_dans_le_document
        == "Quel est le directeur de l'ANSSI ?\nVincent Strubel"
    )


def test_reclassement_llm_retourne_une_meconnaissance_sans_appeler_la_generation_si_aucun_passage_n_est_utile(
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
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
                                {
                                    "id": 1,
                                    "categorie": "preuve_principale",
                                    "id_segment_probant": 1,
                                    "adequation_document": "consacre_au_sujet",
                                    "degre_pertinence": 3,
                                    "portee_preuve": "specifique_non_demandee",
                                }
                            ],
                            "ids_retenus": [],
                        }
                    )
                )
                .construis()
            ]
        ]
    )

    reponse = un_service_albert_de_test(
        une_configuration_de_service_albert(type_reclasseur=TypeReclasseur.LLM),
        client,
        reclasseur=ReclasseurLLM(client, "", BusEvenementsEnMemoire()),
        executeur_de_requetes=None,
    ).pose_question(question="Question ?")

    assert reponse.violation == ViolationMeconnaissance()
    assert reponse.paragraphes == []
    assert len(client.messages_envoyes_pour_les_propositions) == 1


def test_reclasseur_filtre_les_reponses_maitrisees(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
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
    service = un_service_albert_de_test(
        une_configuration_de_service_albert(type_reclasseur=TypeReclasseur.LLM),
        client,
        mapping_reponses=MappingReponsesMaitrisees(
            {"reponse-maitrisee": "La réponse maîtrisée complète."}
        ),
        reclasseur=un_reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    )

    reponse = service.pose_question(question="Question ?")

    assert [p.contenu for p in reponse.paragraphes] == ["Réponse maîtrisée"]


def test_reclasseur_ne_filtre_pas_les_reponses_maitrisees_sous_le_seuil(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
    un_service_albert_de_test,
):
    reclasseur = un_reclasseur
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
    service = un_service_albert_de_test(
        une_configuration_de_service_albert(
            type_reclasseur=TypeReclasseur.LLM, seuil_reponse_maitrisee=1.1
        ),
        client,
        mapping_reponses=MappingReponsesMaitrisees(
            {"reponse-maitrisee": "La réponse maîtrisée complète."}
        ),
        reclasseur=reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
    )

    reponse = service.pose_question(question="Question ?")

    assert [p.contenu for p in reponse.paragraphes] == [
        "Réponse maîtrisée",
        "Autre preuve",
    ]
