from concurrent.futures import Executor, Future, ThreadPoolExecutor

import pytest
from typing import cast, Any

from adaptateurs.bus_evenements import BusEvenementsEnMemoire, ErreurTechniqueSurvenue
from classification_de_test import (
    classification_element_de_reponse,
    reponse_classification_avec_identifiants_globaux, classification_preuve_principale,
)
from client_albert_de_test import ClientAlbertMemoire, un_choix_de_proposition
from configuration import CapaciteReclassementParallele
from question.reclassement.contrat_reclassement_llm import schema_classification
from reclassement_llm_support import un_reclasseur_qui_repond
from reclassement_parallele_support import (
    ClientAlbertLotsEnOrdreControle,
    ClientAlbertQuiEchoueAuDeuxiemeLot,
)
from schemas.albert import ParagrapheReponseMaitrisee
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
    ErreurSaturationReclassement,
)
from services.exceptions import ErreurCommunicationModeleReclassement
from services.reclasseur_llm_en_parallele import ReclasseurLLMEnParallele
from unites_source_de_test import une_unite_source, une_table_des_matieres


@pytest.fixture
def un_coordinateur_reclassement():
    coordinateur = CoordinateurReclassementParallele(ThreadPoolExecutor(max_workers=5))
    yield coordinateur
    coordinateur.ferme()


def reponse_sans_preuve_pour(identifiants) -> str:
    return reponse_classification_avec_identifiants_globaux(
        {
            identifiant: classification_element_de_reponse()
            for identifiant in identifiants
        }
    )


def test_ne_contacte_pas_le_modele_sans_candidat() -> None:
    reclasseur, client = un_reclasseur_qui_repond()

    resultat = reclasseur.reclasse("Une question ?", [])

    assert resultat.paragraphes_retenus == []
    assert resultat.aucune_source_utile is True
    assert client.messages_envoyes_pour_les_propositions == []


def test_classifie_les_lots_sequentiellement_avec_leur_schema(des_paragraphes) -> None:
    reclasseur, client = un_reclasseur_qui_repond(
        reponse_sans_preuve_pour(range(1, 6)), reponse_sans_preuve_pour([6])
    )
    paragraphes = des_paragraphes(6)

    resultat = reclasseur.reclasse("Une question ?", paragraphes)

    formats = [cast(Any, f)["json_schema"] for f in client.formats_reponse_recus]
    assert resultat.tous_les_candidats == paragraphes
    assert [f["name"] for f in formats] == ["classification_passages"] * 2
    assert all(f["strict"] is True for f in formats)
    assert [f["schema"] for f in formats] == [
        schema_classification(paragraphes[:5], premier_id=1),
        schema_classification(paragraphes[5:], premier_id=6),
    ]
    assert client.temperatures_recues == [0, 0]


def test_le_prompt_presente_chaque_candidat_avec_ses_unites(
        un_constructeur_de_paragraphe,
) -> None:
    paragraphe = (
        un_constructeur_de_paragraphe()
        .avec_les_unites_source(
            [
                une_unite_source("Première unité", numero_page=3),
                une_table_des_matieres("Sommaire", numero_page=3),
            ]
        )
        .construis()
    )
    reclasseur, client = un_reclasseur_qui_repond(
        reponse_sans_preuve_pour([1]),
        prompt_classification="{QUESTION}\n{CANDIDATS}",
    )

    reclasseur.reclasse("Une question ?", [paragraphe])

    prompt = str(
        cast(Any, client.messages_envoyes_pour_les_propositions[0][0])["content"]
    )
    assert prompt.startswith("Une question ?\n[PASSAGE id=1 ")
    assert "[UNITE id=1 page=3 type_de_bloc='paragraphe'" in prompt
    assert "[UNITE id=2 page=3 type_de_bloc='table_des_matieres'" in prompt
    assert "Première unité" in prompt


@pytest.mark.parametrize(
    "classification",
    [
        pytest.param(classification_element_de_reponse(), id="element_de_reponse"),
        pytest.param(
            classification_element_de_reponse(
                relation="indirecte", apport="reponse_centrale"
            ),
            id="complement_indirect",
        ),
    ],
)
def test_ne_retient_aucun_paragraphe_sans_preuve_principale(
        des_paragraphes, classification
) -> None:
    reclasseur, _ = un_reclasseur_qui_repond(
        reponse_classification_avec_identifiants_globaux({1: classification})
    )
    candidats = des_paragraphes(1)

    resultat = reclasseur.reclasse("Une question ?", candidats)

    assert resultat.paragraphes_retenus == []
    assert resultat.tous_les_candidats == candidats
    assert resultat.aucune_source_utile is True


def test_ne_reclasse_aucun_candidat_sans_preuve_de_portee_admissible(
        des_paragraphes,
) -> None:
    reclasseur, _ = un_reclasseur_qui_repond(
        reponse_classification_avec_identifiants_globaux(
            {
                1: classification_preuve_principale(
                    portee="specifique_non_demandee", apport="reponse_centrale"
                ),
                2: classification_element_de_reponse(),
            }
        )
    )
    candidats = des_paragraphes(2)

    resultat = reclasseur.reclasse("Une question ?", candidats)

    assert resultat.paragraphes_retenus == []
    assert resultat.tous_les_candidats == candidats
    assert resultat.aucune_source_utile is True


def test_fusionne_les_preuves_et_conserve_les_candidats_originaux(
        un_constructeur_de_paragraphe_reponse_maitrisee,
) -> None:
    reclasseur, _ = un_reclasseur_qui_repond(
        reponse_classification_avec_identifiants_globaux(
            {1: classification_preuve_principale()}
        )
    )
    paragraphe = un_constructeur_de_paragraphe_reponse_maitrisee().construis()

    resultat = reclasseur.reclasse("Une question ?", [paragraphe])

    retenu = resultat.paragraphes_retenus[0]
    assert retenu.contenu == paragraphe.contenu
    assert retenu.score_reclassement == 1.0
    assert isinstance(retenu, ParagrapheReponseMaitrisee)
    assert resultat.tous_les_candidats == [paragraphe]


def test_cite_la_page_de_l_unite_probante_designee_par_le_modele(
        un_constructeur_de_paragraphe,
) -> None:
    paragraphe = (
        un_constructeur_de_paragraphe()
        .a_la_page(33)
        .avec_les_unites_source(
            [une_unite_source(numero_page=page) for page in (33, 34, 35)]
        )
        .construis()
    )
    reclasseur, _ = un_reclasseur_qui_repond(
        reponse_classification_avec_identifiants_globaux(
            {1: classification_preuve_principale(unite_probante=3)}
        )
    )

    resultat = reclasseur.reclasse("Une question ?", [paragraphe])

    assert [p.numero_page for p in resultat.paragraphes_retenus] == [35]


def test_reunit_toutes_les_preuves_du_degre_maximal_sur_tous_les_lots(
        des_paragraphes,
) -> None:
    def reponse_pour(identifiants: range) -> str:
        return reponse_classification_avec_identifiants_globaux(
            {
                identifiant: classification_preuve_principale(
                    apport="reponse_centrale"
                    if identifiant <= 8
                    else "explication_directe"
                )
                for identifiant in identifiants
            }
        )

    reclasseur, client = un_reclasseur_qui_repond(
        reponse_pour(range(1, 6)),
        reponse_pour(range(6, 11)),
        reponse_pour(range(11, 13)),
    )

    resultat = reclasseur.reclasse("Une question ?", des_paragraphes(12))

    assert [p.contenu for p in resultat.paragraphes_retenus] == [
        f"Passage {identifiant}" for identifiant in range(1, 9)
    ]
    assert len(client.messages_envoyes_pour_les_propositions) == 3


def test_une_reponse_inexploitable_est_signalee_comme_une_erreur_technique(
        des_paragraphes,
) -> None:
    bus = BusEvenementsEnMemoire()
    erreurs: list[ErreurTechniqueSurvenue] = []
    bus.souscris(ErreurTechniqueSurvenue, erreurs.append)
    reclasseur, _ = un_reclasseur_qui_repond("pas du json", bus=bus)

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse("Une question ?", des_paragraphes(1))

    assert isinstance(erreur.value.__cause__, ValueError)
    assert len(erreurs) == 1


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
