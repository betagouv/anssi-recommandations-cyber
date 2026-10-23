import json
import threading
from concurrent.futures import Executor, Future, ThreadPoolExecutor

import pytest

from classification_de_test import (
    classification_preuve_principale,
    reponse_classification_avec_identifiants_globaux,
)
from client_albert_de_test import ClientAlbertMemoire
from configuration import CapaciteReclassementParallele
from reclassement_parallele_support import (
    ClientAlbertAvecQualification,
    ClientAlbertLotsEnOrdreControle,
    ClientAlbertQuiEchoueAuDeuxiemeLot,
    identifiants_candidats,
    un_reclasseur_en_parallele,
)
from schemas.msc import ContexteDocumentMSC
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
    ErreurSaturationReclassement,
)
from services.exceptions import ErreurCommunicationModeleReclassement


@pytest.fixture
def un_coordinateur_reclassement():
    coordinateur = CoordinateurReclassementParallele(ThreadPoolExecutor(max_workers=5))
    yield coordinateur
    coordinateur.ferme()


class ExecuteurSynchrone(Executor):
    def submit(self, fn, /, *args, **kwargs):
        future: Future = Future()
        future.set_result(fn(*args, **kwargs))
        return future


def test_classifie_les_lots_ensemble_avec_des_identifiants_globaux(
    des_paragraphes, un_coordinateur_reclassement
) -> None:
    client = ClientAlbertLotsEnOrdreControle()
    reclasseur = un_reclasseur_en_parallele(
        client, un_coordinateur_reclassement, taille_lot=3
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


def test_qualifie_les_documents_en_meme_temps_que_les_lots(des_paragraphes) -> None:
    class ClientAvecBarriere(ClientAlbertAvecQualification):
        barriere = threading.Barrier(7)

        def recupere_propositions(self, *arguments, **options):
            self.barriere.wait(timeout=5)
            return super().recupere_propositions(*arguments, **options)

    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=7),
        CapaciteReclassementParallele(nombre_maximum_d_appels_par_workflow=7),
    )
    client = ClientAvecBarriere()

    try:
        un_reclasseur_en_parallele(client, coordinateur).reclasse(
            "Question ?", des_paragraphes(28)
        )
    finally:
        coordinateur.ferme()

    assert client.noms_schemas_propositions.count("qualification_guides") == 1
    assert client.noms_schemas_propositions.count("classification_passages") == 6


def test_ne_retient_que_les_preuves_du_document_le_plus_adequat(
    un_constructeur_de_paragraphe,
) -> None:
    class ClientQuiPrefereLeSecondDocument(ClientAlbertAvecQualification):
        def qualifie(self, format_reponse) -> str:
            return json.dumps(
                {"D1": "general_ou_contextuel", "D2": "consacre_au_sujet"}
            )

        def classifie(self, format_reponse) -> str:
            return reponse_classification_avec_identifiants_globaux(
                {
                    identifiant: classification_preuve_principale()
                    for identifiant in identifiants_candidats(format_reponse)
                }
            )

    contexte = ContexteDocumentMSC(nom="Guide", description="Description")
    paragraphes = [
        un_constructeur_de_paragraphe()
        .dans_le_document(document)
        .construis()
        .model_copy(update={"contexte_document_msc": contexte})
        for document in ("general.pdf", "specialise.pdf")
    ]
    coordinateur = CoordinateurReclassementParallele(ExecuteurSynchrone())

    resultat = un_reclasseur_en_parallele(
        ClientQuiPrefereLeSecondDocument(), coordinateur
    ).reclasse("Question ?", paragraphes)

    assert [p.nom_document for p in resultat.paragraphes_retenus] == ["specialise.pdf"]


def test_decrit_chaque_document_dans_le_prompt_de_qualification(
    un_constructeur_de_paragraphe,
) -> None:
    contexte = ContexteDocumentMSC(nom="Guide des mots de passe", description="Texte")
    paragraphe = (
        un_constructeur_de_paragraphe()
        .dans_le_document("mdp.pdf")
        .construis()
        .model_copy(update={"contexte_document_msc": contexte})
    )
    client = ClientAlbertAvecQualification()
    coordinateur = CoordinateurReclassementParallele(ExecuteurSynchrone())

    un_reclasseur_en_parallele(client, coordinateur).reclasse(
        "Ma question ?", [paragraphe]
    )

    prompts = [
        str(messages[0]["content"])
        for messages in client.messages_envoyes_pour_les_propositions
    ]
    assert any(
        prompt.startswith("Ma question ?\n")
        and "Guide des mots de passe" in prompt
        and "mdp.pdf" in prompt
        for prompt in prompts
    )


def test_refuse_un_depassement_de_capacite_avant_tout_appel_modele(
    des_paragraphes,
) -> None:
    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=4),
        CapaciteReclassementParallele(nombre_maximum_d_appels_par_workflow=4),
    )
    client = ClientAlbertMemoire()
    reclasseur = un_reclasseur_en_parallele(client, coordinateur, taille_lot=1)

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse("Question ?", des_paragraphes(4))

    coordinateur.ferme()
    assert isinstance(erreur.value.__cause__, ValueError)
    assert client.messages_envoyes_pour_les_propositions == []


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
    coordinateur = CoordinateurReclassementParallele(
        ExecuteurSynchrone(),
        CapaciteReclassementParallele(nombre_maximum_de_workflows=1),
    )
    reclasseur = un_reclasseur_en_parallele(
        ClientAlbertAvecQualification(), coordinateur
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
    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=6),
        CapaciteReclassementParallele(nombre_maximum_d_appels_par_workflow=6),
    )
    reclasseur = un_reclasseur_en_parallele(client, coordinateur, taille_lot=1)

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
