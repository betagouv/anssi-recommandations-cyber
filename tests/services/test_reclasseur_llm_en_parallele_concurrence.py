import json
from concurrent.futures import ThreadPoolExecutor
import threading

import pytest

from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from client_albert_de_test import ClientAlbertMemoire, un_choix_de_proposition
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
    ErreurSaturationReclassement,
)
from services.reclasseur import ReclasseurLLMEnParallele
from services.exceptions import ErreurCommunicationModeleReclassement
from reclassement_parallele_support import (
    ClientAlbertFenetreQuatreLots,
    ClientAlbertLotsEnOrdreControle,
    ClientAlbertQuiEchoueAuDeuxiemeLot,
    cree_reclasseur_llm_en_parallele,
    reponse_qualification_standard,
)


def test_attribue_des_identifiants_globaux_aux_lots_et_conserve_les_originaux(
    un_constructeur_de_paragraphe, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertLotsEnOrdreControle()
    reclasseur = ReclasseurLLMEnParallele(
        client,
        "{QUESTION}\n{CANDIDATS}",
        BusEvenementsEnMemoire(),
        un_coordinateur_reclassement,
        taille_lot=3,
    )
    paragraphes = [
        un_constructeur_de_paragraphe()
        .avec_contenu(f"preuve {i}")
        .dans_le_document("Guide")
        .construis()
        for i in range(1, 8)
    ]

    with ThreadPoolExecutor(max_workers=1) as executeur_appel:
        appel = executeur_appel.submit(reclasseur.reclasse, "Question ?", paragraphes)
        if not client.demarre.wait(timeout=5):
            exception = appel.exception()
            assert exception is not None
            pytest.fail(
                "Les lots n'ont pas démarré ensemble : "
                f"{type(exception.__cause__).__name__}: {exception.__cause__}"
            )
        for premier_id in (7, 4, 1):
            client.liberations[premier_id].set()
            assert client.termines[premier_id].wait(timeout=5)
        resultat = appel.result(timeout=5)

    assert sorted(client.identifiants_observes) == list(range(1, 8))
    assert [p.contenu for p in resultat.paragraphes_retenus] == [
        f"preuve {i}" for i in range(1, 8)
    ]
    assert resultat.tous_les_candidats == paragraphes


def test_soumet_tous_les_lots_de_plus_de_vingt_candidats_simultanement(
    un_constructeur_de_paragraphe,
) -> None:
    client = ClientAlbertFenetreQuatreLots()
    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=6),
        nombre_maximum_d_appels_par_workflow=6,
        nombre_maximum_de_candidats=21,
    )
    paragraphes = [
        un_constructeur_de_paragraphe()
        .avec_contenu(f"preuve {i}")
        .dans_le_document("Guide")
        .construis()
        for i in range(1, 22)
    ]
    reclasseur = ReclasseurLLMEnParallele(
        client,
        "{CANDIDATS}",
        BusEvenementsEnMemoire(),
        coordinateur,
        taille_lot=5,
    )

    try:
        resultat = reclasseur.reclasse("Question ?", paragraphes)
    finally:
        coordinateur.ferme()

    assert client.nombre_appels == 6
    assert client.maximum_appels_actifs == 6
    assert sorted(client.ids_observes) == list(range(1, 22))
    assert len(resultat.paragraphes_retenus) == 21


def test_soumet_la_qualification_et_tous_les_lots_avant_leurs_reponses(
    un_constructeur_de_paragraphe,
) -> None:
    barriere = threading.Barrier(7)

    class ClientAvecBarriereSurChaqueAppel(ClientAlbertMemoire):
        def recupere_propositions(
            self, messages, modele=None, temperature=None, format_reponse=None
        ):
            nom_schema = format_reponse["json_schema"]["name"]
            self.noms_schemas_propositions.append(nom_schema)
            barriere.wait(timeout=3)
            if nom_schema == "qualification_guides":
                contenu = reponse_qualification_standard(format_reponse)
            else:
                candidats = format_reponse["json_schema"]["schema"]["properties"][
                    "candidats"
                ]["properties"]
                contenu = json.dumps(
                    {
                        "candidats": {
                            identifiant: {
                                "categorie": "element_de_reponse",
                                "relation": "indirecte",
                                "portee": "generale",
                                "apport": "explication_directe",
                            }
                            for identifiant in candidats
                        }
                    }
                )
            return [un_choix_de_proposition().ayant_pour_contenu(contenu).construis()]

    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=7),
        nombre_maximum_d_appels_par_workflow=7,
    )
    client = ClientAvecBarriereSurChaqueAppel()
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, coordinateur, prompt_classification="{CANDIDATS}", taille_lot=5
    )
    paragraphes = [
        un_constructeur_de_paragraphe().avec_contenu(f"passage {index}").construis()
        for index in range(28)
    ]

    try:
        resultat = reclasseur.reclasse("Question ?", paragraphes)
    finally:
        coordinateur.ferme()

    assert len(client.noms_schemas_propositions) == 7
    assert client.noms_schemas_propositions.count("qualification_guides") == 1
    assert client.noms_schemas_propositions.count("classification_passages") == 6
    assert resultat.aucune_source_utile is True


def test_refuse_un_depassement_de_candidats_avant_tout_appel_modele(
    un_constructeur_de_paragraphe,
) -> None:
    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=7),
        nombre_maximum_d_appels_par_workflow=7,
        nombre_maximum_de_candidats=20,
    )
    client = ClientAlbertMemoire()
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, coordinateur, prompt_classification="{CANDIDATS}", taille_lot=5
    )
    paragraphes = [
        un_constructeur_de_paragraphe().avec_contenu(str(index)).construis()
        for index in range(21)
    ]

    try:
        with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
            reclasseur.reclasse("Question ?", paragraphes)
    finally:
        coordinateur.ferme()

    assert isinstance(erreur.value.__cause__, ValueError)
    assert client.messages_envoyes_pour_les_propositions == []


def test_refuse_un_depassement_du_plafond_d_appels_avant_tout_appel_modele(
    un_constructeur_de_paragraphe,
) -> None:
    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=5),
        nombre_maximum_d_appels_par_workflow=5,
    )
    client = ClientAlbertMemoire()
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, coordinateur, prompt_classification="{CANDIDATS}", taille_lot=1
    )
    paragraphes = [
        un_constructeur_de_paragraphe().avec_contenu(str(index)).construis()
        for index in range(5)
    ]

    try:
        with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
            reclasseur.reclasse("Question ?", paragraphes)
    finally:
        coordinateur.ferme()

    assert isinstance(erreur.value.__cause__, ValueError)
    assert client.messages_envoyes_pour_les_propositions == []


def test_admet_deux_workflows_complets_et_refuse_le_troisieme(
    un_constructeur_de_paragraphe,
) -> None:
    appels_demarrés = threading.Event()
    liberer_appels = threading.Event()
    verrou = threading.Lock()

    class ClientAvecBarriereSurDeuxWorkflows(ClientAlbertMemoire):
        def __init__(self) -> None:
            super().__init__()
            self.appels_actifs = 0
            self.maximum_appels_actifs = 0
            self.nombre_appels = 0

        def recupere_propositions(
            self, messages, modele=None, temperature=None, format_reponse=None
        ):
            nom_schema = format_reponse["json_schema"]["name"]
            with verrou:
                self.nombre_appels += 1
                self.appels_actifs += 1
                self.maximum_appels_actifs = max(
                    self.maximum_appels_actifs, self.appels_actifs
                )
                self.noms_schemas_propositions.append(nom_schema)
                if self.nombre_appels == 14:
                    appels_demarrés.set()
            try:
                assert liberer_appels.wait(timeout=5)
                if nom_schema == "qualification_guides":
                    contenu = reponse_qualification_standard(format_reponse)
                else:
                    candidats = format_reponse["json_schema"]["schema"]["properties"][
                        "candidats"
                    ]["properties"]
                    contenu = json.dumps(
                        {
                            "candidats": {
                                identifiant: {
                                    "categorie": "element_de_reponse",
                                    "relation": "indirecte",
                                    "portee": "generale",
                                    "apport": "explication_directe",
                                }
                                for identifiant in candidats
                            }
                        }
                    )
                return [
                    un_choix_de_proposition().ayant_pour_contenu(contenu).construis()
                ]
            finally:
                with verrou:
                    self.appels_actifs -= 1

    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=14),
        nombre_maximum_de_workflows=2,
        nombre_maximum_d_appels_par_workflow=7,
        nombre_maximum_de_candidats=28,
    )
    client = ClientAvecBarriereSurDeuxWorkflows()
    reclasseur = cree_reclasseur_llm_en_parallele(
        client, coordinateur, prompt_classification="{CANDIDATS}", taille_lot=5
    )
    paragraphes = [
        un_constructeur_de_paragraphe().avec_contenu(f"passage {index}").construis()
        for index in range(28)
    ]

    try:
        with ThreadPoolExecutor(max_workers=2) as executeur_workflows:
            appels = [
                executeur_workflows.submit(
                    reclasseur.reclasse, "Question ?", paragraphes
                )
                for _ in range(2)
            ]
            assert appels_demarrés.wait(timeout=5)
            with pytest.raises(ErreurSaturationReclassement):
                coordinateur.ouvre_workflow()
            liberer_appels.set()
            resultats = [appel.result(timeout=5) for appel in appels]
    finally:
        liberer_appels.set()
        coordinateur.ferme()

    assert client.nombre_appels == 14
    assert client.maximum_appels_actifs == 14
    assert all(resultat.aucune_source_utile for resultat in resultats)


def test_refuse_un_troisieme_reclassement_simultane() -> None:
    coordinateur = CoordinateurReclassementParallele(ThreadPoolExecutor(max_workers=4))
    premier = coordinateur.ouvre_workflow()
    deuxieme = coordinateur.ouvre_workflow()

    with pytest.raises(ErreurSaturationReclassement):
        coordinateur.ouvre_workflow()

    premier.termine()
    deuxieme.termine()
    coordinateur.ferme()


def test_un_echec_de_lot_empeche_de_soumettre_le_lot_suivant() -> None:
    coordinateur = CoordinateurReclassementParallele(ThreadPoolExecutor(max_workers=4))
    workflow = coordinateur.ouvre_workflow()

    def echoue() -> None:
        raise ValueError("échec de lot")

    futur = workflow.soumet(echoue)
    with pytest.raises(ValueError, match="échec de lot"):
        futur.result()

    with pytest.raises(ValueError, match="échec de lot"):
        workflow.soumet(lambda: None)

    workflow.annule_en_attente()
    workflow.termine()
    coordinateur.ferme()


def test_retourne_sur_echec_pendant_qu_un_autre_lot_reste_bloque(
    un_constructeur_de_paragraphe,
) -> None:
    client = ClientAlbertQuiEchoueAuDeuxiemeLot()
    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=6),
        nombre_maximum_d_appels_par_workflow=6,
        nombre_maximum_de_candidats=5,
    )
    reclasseur = ReclasseurLLMEnParallele(
        client,
        "{CANDIDATS}",
        BusEvenementsEnMemoire(),
        coordinateur,
        taille_lot=1,
    )
    paragraphes = [
        un_constructeur_de_paragraphe().avec_contenu(f"passage {i}").construis()
        for i in range(1, 6)
    ]

    with ThreadPoolExecutor(max_workers=1) as executeur_appel:
        appel = executeur_appel.submit(
            reclasseur.reclasse, "Une question ?", paragraphes
        )
        try:
            assert client.tous_les_lots_soumis.wait(timeout=5)
            with pytest.raises(ErreurCommunicationModeleReclassement):
                appel.result(timeout=5)
            assert sorted(client.appels) == [1, 2, 3, 4, 5]
            assert client.appels_en_cours == 4
            deuxieme = coordinateur.ouvre_workflow()
            with pytest.raises(ErreurSaturationReclassement):
                coordinateur.ouvre_workflow()
            deuxieme.termine()
        finally:
            client.liberation.set()
            coordinateur.ferme()
