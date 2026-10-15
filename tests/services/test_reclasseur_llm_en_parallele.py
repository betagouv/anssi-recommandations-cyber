import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import threading

import pytest

from adaptateurs.bus_evenements import (
    BusEvenementsEnMemoire,
    ErreurTechniqueSurvenue,
)
from client_albert_de_test import (
    ClientAlbertMemoire,
    un_choix_de_proposition,
    un_resultat_de_recherche,
)
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest
from services.coordinateur_reclassement_parallele import (
    ErreurSaturationReclassement,
)
from services.reclasseur import ReclasseurLLMEnParallele
from services.selection_reclassement import fusionne_preuves
from schemas.albert import ParagrapheReponseMaitrisee, UniteSource
from schemas.msc import ContexteDocumentMSC
from services.exceptions import ErreurCommunicationModeleReclassement
from services.service_albert import Prompts, ServiceAlbert
from reclassement_parallele_support import (
    ClientAlbertCaptureFormats,
    ClientAlbertQualificationDocumentRetardee,
    classification_element_de_reponse,
    classification_preuve_principale,
    configure_reponses_par_appel,
    cree_reclasseur_llm_en_parallele,
    identifiants_candidats,
    nombre_appels_par_schema,
    reponse_classification_avec_identifiants_globaux,
)


def test_ne_contacte_pas_le_modele_sans_candidat(un_coordinateur_reclassement) -> None:
    client = ClientAlbertMemoire()
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
    )

    resultat = reclasseur.reclasse("Une question ?", [])

    assert resultat.paragraphes_retenus == []
    assert resultat.tous_les_candidats == []
    assert resultat.aucune_source_utile is True
    assert client.messages_envoyes_pour_les_propositions == []


def test_exige_un_coordinateur_partage_pour_le_mode_parallele() -> None:
    with pytest.raises(ValueError, match="coordinateur"):
        ReclasseurLLMEnParallele(
            ClientAlbertMemoire(), "classification", BusEvenementsEnMemoire()
        )


def test_exige_un_prompt_de_qualification_non_vide(
    un_coordinateur_reclassement,
) -> None:
    with pytest.raises(ValueError, match="prompt de qualification"):
        cree_reclasseur_llm_en_parallele(
            ClientAlbertMemoire(),
            un_coordinateur_reclassement,
            prompt_qualification="  ",
        )


def test_ne_fusionne_pas_les_lots_sans_preuve_principale(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            reponse_classification_avec_identifiants_globaux(
                {1: classification_element_de_reponse()}
            ),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
    )

    resultat = reclasseur.reclasse(
        "Une question ?",
        [un_constructeur_de_paragraphe().avec_contenu("Un passage").construis()],
    )

    assert resultat.paragraphes_retenus == []
    assert resultat.aucune_source_utile is True
    assert nombre_appels_par_schema(client, "classification_passages") == 1


def test_un_complement_indirect_ne_declenche_pas_la_generation(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            json.dumps(
                {
                    "candidats": {
                        "1": {
                            "categorie": "element_de_reponse",
                            "relation": "indirecte",
                            "portee": "generale",
                            "apport": "reponse_centrale",
                        }
                    },
                }
            ),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, un_coordinateur_reclassement, prompt_classification="classification"
    )

    resultat = reclasseur.reclasse(
        "Question ?",
        [un_constructeur_de_paragraphe().avec_contenu("Contexte").construis()],
    )

    assert resultat.paragraphes_retenus == []
    assert resultat.aucune_source_utile is True
    assert nombre_appels_par_schema(client, "classification_passages") == 1


def test_fusionne_les_preuves_et_conserve_les_candidats_originaux(
    un_constructeur_de_paragraphe_reponse_maitrisee, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            reponse_classification_avec_identifiants_globaux(
                {1: classification_preuve_principale()}
            ),
            json.dumps({"1": 1}),
        ],
    )
    paragraphe = (
        un_constructeur_de_paragraphe_reponse_maitrisee()
        .avec_contenu("R5 Protéger les comptes.")
        .construis()
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
    )

    resultat = reclasseur.reclasse("Une question ?", [paragraphe])

    assert [p.contenu for p in resultat.paragraphes_retenus] == [
        "R5 Protéger les comptes."
    ]
    assert resultat.paragraphes_retenus[0].score_reclassement == 1.0
    assert isinstance(resultat.paragraphes_retenus[0], ParagrapheReponseMaitrisee)
    assert resultat.tous_les_candidats == [paragraphe]
    assert nombre_appels_par_schema(client, "classification_passages") == 1


def test_demande_un_schema_de_classification_exact_par_identifiant(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertCaptureFormats()
    configure_reponses_par_appel(
        client,
        [
            reponse_classification_avec_identifiants_globaux(
                {1: classification_preuve_principale()}
            ),
            json.dumps({"1": 1}),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
    )

    reclasseur.reclasse(
        "Une question ?",
        [un_constructeur_de_paragraphe().avec_contenu("Passage").construis()],
    )

    index_classification = client.noms_schemas_propositions.index(
        "classification_passages"
    )
    schema = client.formats_reponse_recus[index_classification]
    assert schema is not None
    schema = schema["json_schema"]["schema"]
    assert schema["required"] == ["candidats"]
    assert schema["additionalProperties"] is False
    assert schema["properties"]["candidats"]["additionalProperties"] is False
    evaluation = schema["properties"]["candidats"]["properties"]["1"]
    assert len(evaluation["anyOf"]) == 2
    branche_complement, branche_preuve = evaluation["anyOf"]
    assert branche_preuve["required"] == [
        "categorie",
        "relation",
        "portee",
        "apport",
        "debut_unite",
        "fin_unite",
    ]
    assert branche_preuve["properties"]["debut_unite"]["enum"] == [1]
    assert branche_preuve["properties"]["portee"]["enum"] == [
        "generale",
        "specifique_demandee",
        "specifique_non_demandee",
    ]
    assert branche_preuve["properties"]["categorie"]["const"] == "preuve_principale"
    assert branche_complement["required"] == [
        "categorie",
        "relation",
        "portee",
        "apport",
    ]
    assert branche_complement["properties"]["categorie"]["enum"] == [
        "hors_sujet",
        "dans_la_thematique_sans_apport",
        "element_de_reponse",
    ]


def test_un_candidat_sans_unite_substantielle_ne_peut_pas_etre_une_preuve(
    un_constructeur_de_paragraphe,
) -> None:
    paragraphe = un_constructeur_de_paragraphe().avec_contenu(" \n\t ").construis()

    schema = ReclasseurLLMEnParallele._schema_classification([paragraphe], 1)

    assert len(schema["properties"]["candidats"]["properties"]["1"]["anyOf"]) == 1
    branche_complement = schema["properties"]["candidats"]["properties"]["1"]["anyOf"][
        0
    ]
    assert branche_complement["properties"]["categorie"]["enum"] == [
        "hors_sujet",
        "dans_la_thematique_sans_apport",
        "element_de_reponse",
    ]


def test_schema_force_l_adequation_indetermine_si_le_document_n_est_pas_qualifie(
    un_constructeur_de_paragraphe,
) -> None:
    schema = ReclasseurLLMEnParallele._schema_qualification_documents(
        {"D1": {"nom_fichier": "guide.pdf", "nom": "", "description": ""}}
    )

    assert schema["properties"]["D1"]["enum"] == ["indetermine"]


@pytest.mark.parametrize(
    "qualification",
    [
        {},
        {"D2": "indetermine"},
        {"D1": "valeur_inconnue"},
        {"D1": {"adequation_document": "indetermine"}},
    ],
)
def test_rejette_une_qualification_de_document_incomplete_ou_invalide(
    un_constructeur_de_paragraphe,
    un_coordinateur_reclassement,
    qualification: dict,
) -> None:
    classification_prete = threading.Event()

    class ClientAvecQualificationInvalide(ClientAlbertMemoire):
        def recupere_propositions(
            self, messages, modele=None, temperature=None, format_reponse=None
        ):
            nom_schema = format_reponse["json_schema"]["name"]
            if nom_schema == "qualification_guides":
                assert classification_prete.wait(timeout=5)
                self.reponse_qualification_documents = json.dumps(qualification)
                return super().recupere_propositions(
                    messages, modele, temperature, format_reponse
                )
            classification_prete.set()
            return super().recupere_propositions(
                messages, modele, temperature, format_reponse
            )

    client = ClientAvecQualificationInvalide()
    configure_reponses_par_appel(
        client,
        [
            json.dumps(
                {
                    "candidats": {
                        "1": {
                            "categorie": "element_de_reponse",
                            "relation": "directe",
                            "portee": "generale",
                            "apport": "principe_direct",
                        }
                    },
                }
            ),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, un_coordinateur_reclassement, prompt_classification="classification"
    )

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse(
            "Question ?",
            [un_constructeur_de_paragraphe().avec_contenu("Contenu").construis()],
        )

    assert isinstance(erreur.value.__cause__, ValueError)
    assert "qualification" in str(erreur.value.__cause__)
    assert nombre_appels_par_schema(client, "qualification_guides") == 1


def test_echec_de_qualification_garde_l_admission_jusqu_a_la_fin_du_lot_en_cours(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    lot_demarre = threading.Event()
    terminer_lot = threading.Event()

    class ClientAvecQualificationInvalide(ClientAlbertMemoire):
        def recupere_propositions(
            self, messages, modele=None, temperature=None, format_reponse=None
        ):
            nom_schema = format_reponse["json_schema"]["name"]
            self.noms_schemas_propositions.append(nom_schema)
            if nom_schema == "qualification_guides":
                assert lot_demarre.wait(timeout=5)
                contenu = json.dumps({})
            else:
                lot_demarre.set()
                assert terminer_lot.wait(timeout=5)
                contenu = json.dumps(
                    {
                        "candidats": {
                            "1": {
                                "categorie": "element_de_reponse",
                                "relation": "indirecte",
                                "portee": "generale",
                                "apport": "principe_direct",
                            }
                        }
                    }
                )
            return [un_choix_de_proposition().ayant_pour_contenu(contenu).construis()]

    reclasseur = cree_reclasseur_llm_en_parallele(
        ClientAvecQualificationInvalide(),
        un_coordinateur_reclassement,
        prompt_classification="{QUESTION}\n{CANDIDATS}",
        taille_lot=1,
    )

    with ThreadPoolExecutor(max_workers=1) as executeur_appel:
        appel = executeur_appel.submit(
            reclasseur.reclasse,
            "Question ?",
            [un_constructeur_de_paragraphe().avec_contenu("Passage").construis()],
        )
        assert lot_demarre.wait(timeout=5)
        with pytest.raises(ErreurCommunicationModeleReclassement):
            appel.result(timeout=5)

        workflow_concurrent = un_coordinateur_reclassement.ouvre_workflow()
        try:
            with pytest.raises(ErreurSaturationReclassement):
                un_coordinateur_reclassement.ouvre_workflow()
        finally:
            terminer_lot.set()
            workflow_concurrent.termine()


def test_retient_le_premier_page_substantiel_de_la_plage_sans_reduire_la_source(
    un_coordinateur_reclassement,
) -> None:
    contenu_source = "Table des matières\n\nConsigne utile\n\nAutre consigne"
    paragraphe = ParagrapheReponseMaitrisee(
        contenu=contenu_source,
        reponse="Réponse maîtrisée",
        score_similarite=0.8,
        numero_page=1,
        url="https://exemple.test/source.pdf",
        nom_document="source.pdf",
        unites_source=[
            UniteSource(
                contenu="Table des matières",
                numero_page=1,
                url="https://exemple.test/source.pdf",
                nom_document="source.pdf",
                type_de_bloc="table_des_matieres",
            ),
            UniteSource(
                contenu="Consigne utile",
                numero_page=34,
                url="https://exemple.test/source.pdf",
                nom_document="source.pdf",
                type_de_bloc="paragraphe",
            ),
            UniteSource(
                contenu="Table des matières encore",
                numero_page=34,
                url="https://exemple.test/source.pdf",
                nom_document="source.pdf",
                type_de_bloc="table_des_matieres",
            ),
            UniteSource(
                contenu="Autre consigne",
                numero_page=35,
                url="https://exemple.test/source.pdf",
                nom_document="source.pdf",
                type_de_bloc="paragraphe",
            ),
        ],
    )
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            json.dumps(
                {
                    "candidats": {
                        "1": {
                            "categorie": "preuve_principale",
                            "relation": "directe",
                            "portee": "generale",
                            "apport": "explication_directe",
                            "debut_unite": 2,
                            "fin_unite": 4,
                        }
                    },
                }
            ),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, un_coordinateur_reclassement, prompt_classification="classification"
    )

    resultat = reclasseur.reclasse("Question ?", [paragraphe])

    assert len(resultat.paragraphes_retenus) == 1
    source = resultat.paragraphes_retenus[0]
    assert isinstance(source, ParagrapheReponseMaitrisee)
    assert source.numero_page == 34
    assert source.contenu == contenu_source
    assert source.reponse == "Réponse maîtrisée"
    assert source.score_reclassement == 1.0


@pytest.mark.parametrize(("debut_unite", "fin_unite"), [(1, 2), (2, 3)])
def test_rejette_une_borne_de_preuve_placee_sur_une_table_des_matieres(
    un_constructeur_de_paragraphe,
    un_coordinateur_reclassement,
    debut_unite: int,
    fin_unite: int,
) -> None:
    paragraphe = un_constructeur_de_paragraphe().avec_contenu("source").construis()
    paragraphe = paragraphe.model_copy(
        update={
            "unites_source": [
                UniteSource(
                    contenu="Sommaire",
                    numero_page=1,
                    url=paragraphe.url,
                    nom_document=paragraphe.nom_document,
                    type_de_bloc="table_des_matieres",
                ),
                UniteSource(
                    contenu="Prescription",
                    numero_page=2,
                    url=paragraphe.url,
                    nom_document=paragraphe.nom_document,
                    type_de_bloc="paragraphe",
                ),
                UniteSource(
                    contenu="Sommaire intercalaire",
                    numero_page=2,
                    url=paragraphe.url,
                    nom_document=paragraphe.nom_document,
                    type_de_bloc="table_des_matieres",
                ),
                UniteSource(
                    contenu="Condition",
                    numero_page=3,
                    url=paragraphe.url,
                    nom_document=paragraphe.nom_document,
                    type_de_bloc="paragraphe",
                ),
            ]
        }
    )
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            json.dumps(
                {
                    "candidats": {
                        "1": {
                            "categorie": "preuve_principale",
                            "relation": "directe",
                            "portee": "generale",
                            "apport": "reponse_centrale",
                            "debut_unite": debut_unite,
                            "fin_unite": fin_unite,
                        }
                    },
                }
            ),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, un_coordinateur_reclassement, prompt_classification="classification"
    )

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse("Question ?", [paragraphe])

    assert isinstance(erreur.value.__cause__, ValueError)
    assert "plage" in str(erreur.value.__cause__)


def test_applique_la_adequation_du_document_proprietaire_aux_lots_suivants(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertQualificationDocumentRetardee()
    contexte = ContexteDocumentMSC(
        nom="Guide spécialisé",
        description="Guide consacré au sujet.",
        nom_fichier="Guide spécialisé",
    )
    paragraphes = [
        un_constructeur_de_paragraphe()
        .avec_contenu(f"Passage {identifiant}")
        .dans_le_document("Guide spécialisé")
        .construis()
        .model_copy(update={"contexte_document_msc": contexte})
        for identifiant in (1, 2)
    ]
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
        prompt_classification=Path(
            "templates/prompt_reclassement_llm_parallele_classification.txt"
        ).read_text(encoding="utf-8"),
        taille_lot=1,
        prompt_qualification=Path(
            "templates/prompt_reclassement_llm_parallele_qualification.txt"
        ).read_text(encoding="utf-8"),
    )

    resultat = reclasseur.reclasse("Question ?", paragraphes)

    assert client.ordre_fin_lots == [2, 1]
    assert [p.contenu for p in resultat.paragraphes_retenus] == ["Passage 2"]


def test_qualifie_chaque_guide_une_fois_hors_des_lots_de_passages(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
):
    class ClientQuiRepondSelonLeSchema(ClientAlbertMemoire):
        def __init__(self):
            super().__init__()
            self.noms_schemas = []

        def recupere_propositions(
            self, messages, modele=None, temperature=None, format_reponse=None
        ):
            nom_schema = format_reponse["json_schema"]["name"]
            self.noms_schemas.append(nom_schema)
            proprietes = format_reponse["json_schema"]["schema"]["properties"]
            if nom_schema == "qualification_guides":
                contenu = json.dumps(
                    {identifiant: "consacre_au_sujet" for identifiant in proprietes}
                )
            else:
                identifiants = proprietes["candidats"]["properties"]
                contenu = json.dumps(
                    {
                        "candidats": {
                            identifiant: {
                                "categorie": "element_de_reponse",
                                "relation": "indirecte",
                                "portee": "generale",
                                "apport": "principe_direct",
                            }
                            for identifiant in identifiants
                        }
                    }
                )
            return [un_choix_de_proposition().ayant_pour_contenu(contenu).construis()]

    client = ClientQuiRepondSelonLeSchema()
    guide = "Guide spécialisé"
    contexte = ContexteDocumentMSC(
        nom="Guide sur les mots de passe",
        description="Recommandations d'authentification et de stockage.",
        nom_fichier=guide,
    )
    paragraphes = [
        un_constructeur_de_paragraphe()
        .avec_contenu(f"Passage {identifiant}")
        .dans_le_document(guide)
        .construis()
        .model_copy(update={"contexte_document_msc": contexte})
        for identifiant in (1, 2)
    ]
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
        prompt_classification="{QUESTION}\n{CANDIDATS}",
        taille_lot=1,
    )

    reclasseur.reclasse("Comment stocker un mot de passe ?", paragraphes)

    assert len(client.noms_schemas) == 3
    assert client.noms_schemas.count("qualification_guides") == 1
    assert client.noms_schemas.count("classification_passages") == 2


def test_qualification_associe_directement_chaque_identifiant_a_son_label(
    un_coordinateur_reclassement,
):
    class ClientQuiRetourneUneQualificationCompacte(ClientAlbertMemoire):
        def __init__(self):
            super().__init__()
            self.schema_qualification = None

        def recupere_propositions(
            self, messages, modele=None, temperature=None, format_reponse=None
        ):
            self.schema_qualification = format_reponse["json_schema"]["schema"]
            return [
                un_choix_de_proposition()
                .ayant_pour_contenu(json.dumps({"D1": "consacre_au_sujet"}))
                .construis()
            ]

    client = ClientQuiRetourneUneQualificationCompacte()
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
        prompt_classification="{QUESTION}\n{CANDIDATS}",
    )

    qualifications = reclasseur._qualifie_documents(
        "Question ?",
        {
            "D1": {
                "nom_fichier": "guide.pdf",
                "nom": "Guide spécialisé",
                "description": "Description lisible.",
            }
        },
    )

    assert qualifications == {"D1": "consacre_au_sujet"}
    assert client.schema_qualification["required"] == ["D1"]
    assert "documents" not in client.schema_qualification["properties"]


def test_description_html_sans_texte_visible_force_une_qualification_indeterminee(
    un_coordinateur_reclassement,
):
    class ClientQuiObserveLaQualification(ClientAlbertMemoire):
        def __init__(self):
            super().__init__()
            self.schema_qualification = None

        def recupere_propositions(
            self, messages, modele=None, temperature=None, format_reponse=None
        ):
            self.schema_qualification = format_reponse["json_schema"]["schema"]
            return [
                un_choix_de_proposition()
                .ayant_pour_contenu(json.dumps({"D1": "indetermine"}))
                .construis()
            ]

    client = ClientQuiObserveLaQualification()
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
        prompt_classification="{QUESTION}\n{CANDIDATS}",
    )

    qualifications = reclasseur._qualifie_documents(
        "Question ?",
        {
            "D1": {
                "nom_fichier": "guide.pdf",
                "nom": "Guide spécialisé",
                "description": "<p> &nbsp; </p><script>contenu caché</script>",
            }
        },
    )

    assert qualifications == {"D1": "indetermine"}
    assert client.schema_qualification["properties"]["D1"]["enum"] == ["indetermine"]


def test_lit_une_classification_racine_par_identifiant_global(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            reponse_classification_avec_identifiants_globaux(
                {1: classification_element_de_reponse()}
            ),
        ],
    )
    candidats = [
        un_constructeur_de_paragraphe().avec_contenu("Passage utile").construis()
    ]
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
    )

    resultat = reclasseur.reclasse("Question ?", candidats)

    assert resultat.paragraphes_retenus == []
    assert resultat.tous_les_candidats == candidats
    assert resultat.aucune_source_utile is True


def test_ne_garde_que_les_preuves_du_degre_maximal_et_les_ordonner_par_document(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    classifications = {
        1: classification_preuve_principale(apport="principe_direct"),
        2: classification_preuve_principale(apport="explication_directe"),
        3: classification_preuve_principale(apport="explication_directe"),
        4: classification_preuve_principale(apport="explication_directe"),
        5: classification_preuve_principale(apport="explication_directe"),
    }
    client.avec_une_qualification_de_documents(
        json.dumps(
            {
                "D1": "consacre_au_sujet",
                "D2": "consacre_au_sujet",
                "D3": "consacre_au_sujet",
            }
        )
    )
    configure_reponses_par_appel(
        client,
        [
            reponse_classification_avec_identifiants_globaux(classifications),
        ],
    )
    contextes = {
        document: ContexteDocumentMSC(
            nom=document,
            description="Guide consacré à son sujet.",
            nom_fichier=document,
        )
        for document in ("Guide A", "Guide B", "Guide C")
    }
    paragraphes = [
        un_constructeur_de_paragraphe()
        .avec_contenu(f"Passage {identifiant}")
        .dans_le_document(document)
        .construis()
        .model_copy(update={"contexte_document_msc": contextes[document]})
        for identifiant, document in enumerate(
            ("Guide A", "Guide B", "Guide A", "Guide C", "Guide A"), 1
        )
    ]
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
    )

    resultat = reclasseur.reclasse("Question ?", paragraphes)

    assert [paragraphe.contenu for paragraphe in resultat.paragraphes_retenus] == [
        "Passage 2",
        "Passage 3",
        "Passage 5",
        "Passage 4",
    ]
    assert nombre_appels_par_schema(client, "classification_passages") == 1
    assert resultat.tous_les_candidats == paragraphes
    assert all(
        paragraphe.score_reclassement == 1.0
        for paragraphe in resultat.paragraphes_retenus
    )


def test_un_guide_contextuel_ne_downgrade_pas_les_preuves_d_un_guide_specialise(
    un_constructeur_de_paragraphe,
) -> None:
    paragraphes = [
        un_constructeur_de_paragraphe()
        .avec_contenu(f"Passage {identifiant}")
        .dans_le_document(document)
        .construis()
        for identifiant, document in (
            (1, "Guide specialise"),
            (2, "Guide specialise"),
            (3, "Guide general"),
        )
    ]
    evaluations = [
        {
            "id": 1,
            "id_document": "D1",
            "categorie": "preuve_principale",
            "relation": "directe",
            "portee_preuve": "generale",
            "apport": "explication_directe",
            "degre_pertinence": 2,
            "adequation_document": "consacre_au_sujet",
        },
        {
            "id": 2,
            "id_document": "D1",
            "categorie": "preuve_principale",
            "relation": "directe",
            "portee_preuve": "generale",
            "apport": "explication_directe",
            "degre_pertinence": 2,
            "adequation_document": "consacre_au_sujet",
        },
        {
            "id": 3,
            "id_document": "D2",
            "categorie": "preuve_principale",
            "relation": "directe",
            "portee_preuve": "generale",
            "apport": "explication_directe",
            "degre_pertinence": 2,
            "adequation_document": "general_ou_contextuel",
        },
    ]

    ids_retenus = fusionne_preuves(paragraphes, evaluations)

    assert ids_retenus == [1, 2]


def test_un_degre_superieur_ecarte_une_preuve_degre_inferieur(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    classifications = {
        1: classification_preuve_principale(apport="principe_direct"),
        2: classification_preuve_principale(apport="explication_directe"),
    }
    configure_reponses_par_appel(
        client,
        [
            reponse_classification_avec_identifiants_globaux(classifications),
        ],
    )
    paragraphes = [
        un_constructeur_de_paragraphe()
        .avec_contenu(f"Passage {identifiant}")
        .dans_le_document(document)
        .construis()
        for identifiant, document in ((1, "Guide spécialisé"), (2, "Guide général"))
    ]
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
    )

    resultat = reclasseur.reclasse("Question générale ?", paragraphes)

    assert [p.contenu for p in resultat.paragraphes_retenus] == [
        "Passage 2",
    ]


def test_reunit_toutes_les_preuves_du_degre_maximal_sur_tous_les_lots(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    class ClientLotInitialRetarde(ClientAlbertMemoire):
        def __init__(self):
            super().__init__()
            self.autre_lot_a_commence = threading.Event()

        def recupere_propositions(
            self, messages, modele=None, temperature=None, format_reponse=None
        ):
            if format_reponse["json_schema"]["name"] == "classification_passages":
                ids_candidats = identifiants_candidats(format_reponse)
                if ids_candidats[0] == 1:
                    assert self.autre_lot_a_commence.wait(timeout=5)
                else:
                    self.autre_lot_a_commence.set()
            return super().recupere_propositions(
                messages, modele, temperature, format_reponse
            )

    client = ClientLotInitialRetarde()
    reponses_par_identifiants = {}
    for debut, fin in ((1, 6), (6, 11), (11, 13)):
        classifications = {
            identifiant: classification_preuve_principale(
                apport=(
                    "reponse_centrale" if identifiant <= 8 else "explication_directe"
                )
            )
            for identifiant in range(debut, fin)
        }
        reponses_par_identifiants[tuple(range(debut, fin))] = [
            un_choix_de_proposition()
            .ayant_pour_contenu(
                reponse_classification_avec_identifiants_globaux(classifications)
            )
            .construis()
        ]
    client.avec_les_propositions_par_identifiants(reponses_par_identifiants)
    paragraphes = [
        un_constructeur_de_paragraphe()
        .avec_contenu(f"Passage {identifiant}")
        .construis()
        for identifiant in range(1, 13)
    ]
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
    )

    resultat = reclasseur.reclasse("Question ?", paragraphes)

    assert [p.contenu for p in resultat.paragraphes_retenus] == [
        f"Passage {identifiant}" for identifiant in range(1, 9)
    ]
    assert nombre_appels_par_schema(client, "classification_passages") == 3


def test_une_preuve_specifique_non_demandee_ne_bloque_pas_le_repli_general(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    classifications: dict[int, dict[str, str | int]] = {
        1: classification_preuve_principale(
            portee="specifique_non_demandee", apport="reponse_centrale"
        ),
        2: classification_preuve_principale(apport="explication_directe"),
    }
    configure_reponses_par_appel(
        client,
        [
            reponse_classification_avec_identifiants_globaux(classifications),
        ],
    )
    paragraphes = [
        un_constructeur_de_paragraphe().avec_contenu(f"Passage {i}").construis()
        for i in (1, 2)
    ]
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, un_coordinateur_reclassement, prompt_classification="classification"
    )

    resultat = reclasseur.reclasse("Question ?", paragraphes)

    assert [p.contenu for p in resultat.paragraphes_retenus] == ["Passage 2"]


def test_sans_preuve_de_portee_admissible_ne_reclasse_aucun_candidat(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    classifications: dict[int, dict[str, str | int]] = {
        1: classification_preuve_principale(
            portee="specifique_non_demandee", apport="reponse_centrale"
        ),
        2: classification_element_de_reponse(),
    }
    configure_reponses_par_appel(
        client,
        [
            reponse_classification_avec_identifiants_globaux(classifications),
        ],
    )
    paragraphes = [
        un_constructeur_de_paragraphe().avec_contenu(f"Passage {i}").construis()
        for i in (1, 2)
    ]
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, un_coordinateur_reclassement, prompt_classification="classification"
    )

    resultat = reclasseur.reclasse("Question ?", paragraphes)

    assert resultat.paragraphes_retenus == []
    assert resultat.tous_les_candidats == paragraphes
    assert resultat.aucune_source_utile is True


@pytest.mark.parametrize(
    ("categorie", "debut_unite", "fin_unite"),
    [
        ("preuve_principale", 2, 2),
        ("preuve_principale", True, 1),
        ("element_de_reponse", 1, 1),
    ],
)
def test_rejette_une_plage_de_preuve_invalide(
    un_constructeur_de_paragraphe,
    un_coordinateur_reclassement,
    categorie: str,
    debut_unite: int,
    fin_unite: int,
) -> None:
    classification: dict[str, str | int] = {
        "categorie": categorie,
        "relation": "directe",
        "portee": "generale",
        "apport": "principe_direct",
    }
    if categorie == "preuve_principale":
        classification["debut_unite"] = debut_unite
        classification["fin_unite"] = fin_unite
    elif debut_unite:
        classification["debut_unite"] = debut_unite
        classification["fin_unite"] = fin_unite
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            json.dumps(
                {
                    "candidats": {"1": classification},
                }
            ),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
        taille_lot=1,
    )

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse(
            "Une question ?",
            [
                un_constructeur_de_paragraphe()
                .avec_contenu("texte source exact")
                .construis()
            ],
        )

    assert isinstance(erreur.value.__cause__, ValueError)
    assert (
        "classification" in str(erreur.value.__cause__).lower()
        or "plage" in str(erreur.value.__cause__).lower()
    )
    assert nombre_appels_par_schema(client, "classification_passages") == 1


@pytest.mark.parametrize(
    ("champ", "valeur", "message_erreur"),
    [
        ("relation", "inconnue", "La relation du candidat est invalide."),
        ("portee", "inconnue", "La portée de la preuve est invalide."),
        ("apport", "inconnu", "L'apport du candidat est invalide."),
        ("inattendu", "valeur", "Les champs d'une classification sont invalides."),
    ],
)
def test_rejette_une_classification_invalide(
    un_constructeur_de_paragraphe,
    un_coordinateur_reclassement,
    champ: str,
    valeur: str,
    message_erreur: str,
) -> None:
    evaluation = {
        "categorie": "preuve_principale",
        "relation": "directe",
        "portee": "generale",
        "apport": "principe_direct",
        "debut_unite": 1,
        "fin_unite": 1,
    }
    evaluation[champ] = valeur
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            json.dumps({"candidats": {"1": evaluation}}),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
        taille_lot=1,
    )

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse(
            "Une question ?",
            [
                un_constructeur_de_paragraphe()
                .avec_contenu("texte source exact")
                .construis()
            ],
        )

    assert isinstance(erreur.value.__cause__, ValueError)
    assert str(erreur.value.__cause__) == message_erreur
    assert nombre_appels_par_schema(client, "classification_passages") == 1


def test_rejette_un_identifiant_inconnu_et_emet_une_seule_erreur_technique(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            json.dumps(
                {
                    "candidats": {
                        "2": {
                            "categorie": "preuve_principale",
                            "relation": "directe",
                            "portee": "generale",
                            "apport": "reponse_centrale",
                            "debut_unite": 1,
                            "fin_unite": 1,
                        }
                    }
                }
            ),
        ],
    )
    bus = BusEvenementsEnMemoire()
    erreurs: list[ErreurTechniqueSurvenue] = []
    bus.souscris(ErreurTechniqueSurvenue, erreurs.append)
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
        bus=bus,
    )

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse(
            "Une question ?",
            [un_constructeur_de_paragraphe().avec_contenu("Un passage").construis()],
        )

    assert isinstance(erreur.value.__cause__, ValueError)
    assert len(erreurs) == 1
    assert nombre_appels_par_schema(client, "qualification_guides") == 1
    assert nombre_appels_par_schema(client, "classification_passages") == 1


def test_rejette_une_justification_dans_une_classification_de_lot(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            json.dumps(
                {
                    "candidats": {
                        "1": {
                            "categorie": "element_de_reponse",
                            "relation": "indirecte",
                            "portee": "generale",
                            "apport": "principe_direct",
                            "justification_courte": "à supprimer",
                        }
                    }
                }
            ),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
        taille_lot=1,
    )

    with pytest.raises(ErreurCommunicationModeleReclassement):
        reclasseur.reclasse(
            "Une question ?",
            [un_constructeur_de_paragraphe().avec_contenu("Passage").construis()],
        )


def test_rejette_une_cle_inattendue_a_la_racine_de_la_classification(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            json.dumps(
                {
                    "candidats": {
                        "1": {
                            "categorie": "element_de_reponse",
                            "relation": "directe",
                            "portee": "generale",
                            "apport": "principe_direct",
                        }
                    },
                    "metadonnees": {},
                }
            ),
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, un_coordinateur_reclassement, prompt_classification="classification"
    )

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse(
            "Une question ?",
            [un_constructeur_de_paragraphe().avec_contenu("Passage").construis()],
        )

    assert isinstance(erreur.value.__cause__, ValueError)


@pytest.mark.parametrize(
    "contenu",
    [
        '{"candidats":{"1":{"categorie":"element_de_reponse","relation":"directe","portee":"generale","apport":"principe_direct"},"1":{"categorie":"element_de_reponse","relation":"directe","portee":"generale","apport":"principe_direct"}}}',
        '{"candidats":{"1":{"categorie":"element_de_reponse","categorie":"element_de_reponse","relation":"directe","portee":"generale","apport":"principe_direct"}}}',
    ],
)
def test_rejette_les_cles_dupliquees_dans_une_classification_de_lot(
    contenu, un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertMemoire()
    configure_reponses_par_appel(
        client,
        [
            contenu,
        ],
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
        taille_lot=1,
    )

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse(
            "Une question ?",
            [un_constructeur_de_paragraphe().avec_contenu("Passage").construis()],
        )

    assert isinstance(erreur.value.__cause__, ValueError)
    assert str(erreur.value.__cause__) == "La réponse JSON contient une clé dupliquée."


def test_ne_genere_pas_de_reponse_apres_un_echec_de_reclassement_parallele(
    une_configuration_de_service_albert,
    un_adaptateur_executeur_de_requetes,
    un_coordinateur_reclassement,
) -> None:
    class ClientQuiEchoueSurLaClassification(ClientAlbertMemoire):
        def recupere_propositions(
            self, messages, modele=None, temperature=None, format_reponse=None
        ):
            if format_reponse["json_schema"]["name"] == "classification_passages":
                self.noms_schemas_propositions.append("classification_passages")
                raise RuntimeError("échec contrôlé de classification")
            return super().recupere_propositions(
                messages, modele, temperature, format_reponse
            )

    client = ClientQuiEchoueSurLaClassification()
    client.avec_les_resultats(
        [un_resultat_de_recherche().ayant_pour_contenu("Passage").construis()]
    )
    reclasseur = cree_reclasseur_llm_en_parallele(
        client,
        un_coordinateur_reclassement,
        prompt_classification="{QUESTION}\n{CANDIDATS}",
        taille_lot=1,
    )
    service = ServiceAlbert(
        une_configuration_de_service_albert(),
        client,
        False,
        Prompts(prompt_systeme="{chunks}", prompt_reclassement=""),
        reformulateur=ReformulateurDeQuestionDeTest(),
        mapping_reponses=MappingReponsesMaitrisees({}),
        reclasseur=reclasseur,
        executeur_de_requetes=un_adaptateur_executeur_de_requetes,
        bus_evenements=BusEvenementsEnMemoire(),
    )

    with pytest.raises(ErreurCommunicationModeleReclassement):
        service.pose_question(question="Question ?")

    assert client.payload_recu is not None
    assert nombre_appels_par_schema(client, "qualification_guides") == 1
    assert nombre_appels_par_schema(client, "classification_passages") == 1


def test_reclasseur_parallele_est_disponible_depuis_son_module_dedie() -> None:
    from services.reclasseur_llm_en_parallele import (
        ReclasseurLLMEnParallele as ReclasseurDedie,
    )

    assert ReclasseurDedie is ReclasseurLLMEnParallele
