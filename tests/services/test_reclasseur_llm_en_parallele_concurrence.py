from concurrent.futures import Executor, Future, ThreadPoolExecutor

import pytest

from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from classification_de_test import (
    classification_element_de_reponse,
    reponse_classification_avec_identifiants_globaux,
)
from client_albert_de_test import ClientAlbertMemoire, un_choix_de_proposition
from configuration import CapaciteReclassementParallele
from reclassement_parallele_support import (
    ClientAlbertLotsEnOrdreControle,
    ClientAlbertQuiEchoueAuDeuxiemeLot,
)
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
    ErreurSaturationReclassement,
)
from services.exceptions import ErreurCommunicationModeleReclassement
from services.reclasseur_llm_en_parallele import ReclasseurLLMEnParallele


@pytest.fixture
def un_coordinateur_reclassement():
    coordinateur = CoordinateurReclassementParallele(ThreadPoolExecutor(max_workers=5))
    yield coordinateur
    coordinateur.ferme()


def test_classifie_les_lots_ensemble_avec_des_identifiants_globaux(
    des_paragraphes, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertLotsEnOrdreControle()
    reclasseur = ReclasseurLLMEnParallele(
        client,
        "{QUESTION}\n{CANDIDATS}",
        BusEvenementsEnMemoire(),
        un_coordinateur_reclassement,
        taille_lot=3,
    )
    paragraphes = des_paragraphes(7)

    with ThreadPoolExecutor(max_workers=1) as executeur_appel:
        appel = executeur_appel.submit(reclasseur.reclasse, "Question ?", paragraphes)
        assert client.demarre.wait(timeout=5)
        for premier_id in (7, 4, 1):
            client.liberations[premier_id].set()
            assert client.termines[premier_id].wait(timeout=5)
        resultat = appel.result(timeout=5)

    assert sorted(client.identifiants_observes) == list(range(1, 8))
    assert [p.contenu for p in resultat.paragraphes_retenus] == [
        p.contenu for p in paragraphes
    ]
    assert resultat.tous_les_candidats == paragraphes


def test_refuse_un_depassement_de_capacite_avant_tout_appel_modele(
    des_paragraphes,
) -> None:
    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=4),
        CapaciteReclassementParallele(nombre_maximum_d_appels_par_workflow=4),
    )
    client = ClientAlbertMemoire()
    reclasseur = ReclasseurLLMEnParallele(
        client,
        "{CANDIDATS}",
        BusEvenementsEnMemoire(),
        coordinateur,
        taille_lot=1,
    )

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse("Question ?", des_paragraphes(5))

    coordinateur.ferme()
    assert isinstance(erreur.value.__cause__, ValueError)
    assert client.messages_envoyes_pour_les_propositions == []


class ExecuteurSynchrone(Executor):
    def submit(self, fn, /, *args, **kwargs):
        future: Future = Future()
        future.set_result(fn(*args, **kwargs))
        return future


def test_garde_sa_place_jusqu_a_la_fin_du_reclassement() -> None:
    coordinateur = CoordinateurReclassementParallele(ExecuteurSynchrone())
    workflow = coordinateur.ouvre_workflow()
    workflow.soumet(int)
    coordinateur.ouvre_workflow()

    with pytest.raises(ErreurSaturationReclassement):
        coordinateur.ouvre_workflow()

    workflow.termine()
    coordinateur.ouvre_workflow()


def test_libere_sa_place_apres_chaque_reclassement(des_paragraphes) -> None:
    client = ClientAlbertMemoire()
    client.avec_les_propositions_par_appel(
        [
            [
                un_choix_de_proposition()
                .ayant_pour_contenu(
                    reponse_classification_avec_identifiants_globaux(
                        {1: classification_element_de_reponse()}
                    )
                )
                .construis()
            ]
        ]
        * 2
    )
    coordinateur = CoordinateurReclassementParallele(
        ExecuteurSynchrone(),
        CapaciteReclassementParallele(nombre_maximum_de_workflows=1),
    )
    reclasseur = ReclasseurLLMEnParallele(
        client, "{CANDIDATS}", BusEvenementsEnMemoire(), coordinateur
    )

    reclasseur.reclasse("Question ?", des_paragraphes(1))
    reclasseur.reclasse("Question ?", des_paragraphes(1))


def test_la_fermeture_arrete_l_executeur_et_refuse_de_nouveaux_reclassements() -> None:
    executeur = ThreadPoolExecutor(max_workers=1)
    coordinateur = CoordinateurReclassementParallele(executeur)

    coordinateur.ferme()

    with pytest.raises(RuntimeError):
        executeur.submit(int)
    with pytest.raises(ErreurSaturationReclassement):
        coordinateur.ouvre_workflow()


def test_retourne_sur_echec_pendant_qu_un_autre_lot_reste_bloque(
    des_paragraphes,
) -> None:
    client = ClientAlbertQuiEchoueAuDeuxiemeLot()
    coordinateur = CoordinateurReclassementParallele(ThreadPoolExecutor(max_workers=6))
    reclasseur = ReclasseurLLMEnParallele(
        client,
        "{CANDIDATS}",
        BusEvenementsEnMemoire(),
        coordinateur,
        taille_lot=1,
    )

    with ThreadPoolExecutor(max_workers=1) as executeur_appel:
        appel = executeur_appel.submit(
            reclasseur.reclasse, "Une question ?", des_paragraphes(5)
        )
        try:
            assert client.tous_les_lots_soumis.wait(timeout=5)
            with pytest.raises(ErreurCommunicationModeleReclassement):
                appel.result(timeout=5)
            assert client.appels_en_cours == 4
            coordinateur.ouvre_workflow()
            with pytest.raises(ErreurSaturationReclassement):
                coordinateur.ouvre_workflow()
        finally:
            client.liberation.set()
            coordinateur.ferme()
