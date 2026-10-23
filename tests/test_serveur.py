import pytest
from starlette.testclient import TestClient

from adaptateurs.bus_evenements import BusEvenementsEnMemoire, ErreurTechniqueSurvenue
from adaptateurs.sentry import AdaptateurSentryMemoire
from configuration import Mode, CapaciteReclassementParallele
from serveur import fabrique_serveur
from services.coordinateur_reclassement_parallele import fabrique_coordinateur_reclassement, \
    CoordinateurReclassementParallele, ErreurSaturationReclassement


def test_fabrique_serveur_abonne_le_consommateur_sentry_au_bus(pages_statiques):
    bus = BusEvenementsEnMemoire()
    adaptateur_sentry = AdaptateurSentryMemoire()
    fabrique_serveur(
        600,
        Mode.TEST,
        f"{pages_statiques}/ui/dist/",
        lambda: "1",
        lambda: adaptateur_sentry,
        bus_evenements=bus,
    )
    exception = RuntimeError("boom")

    bus.publie(ErreurTechniqueSurvenue(exception=exception, contexte="génération"))

    assert adaptateur_sentry.exceptions_capturees == [exception]

def test_serveur_possede_et_ferme_le_coordinateur_dans_son_cycle_de_vie(
        pages_statiques,
) -> None:
    serveur = fabrique_serveur(600, Mode.TEST, f"{pages_statiques}/ui/dist/")

    with TestClient(serveur):
        coordinateur = fabrique_coordinateur_reclassement()
        assert isinstance(coordinateur, CoordinateurReclassementParallele)

    with pytest.raises(ErreurSaturationReclassement):
        coordinateur.ouvre_workflow()


def test_le_coordinateur_du_serveur_utilise_la_capacite_demandee(
        pages_statiques,
) -> None:
    capacite = CapaciteReclassementParallele(nombre_maximum_d_appels_par_workflow=8)
    serveur = fabrique_serveur(
        600,
        Mode.TEST,
        f"{pages_statiques}/ui/dist/",
        capacite_reclassement=capacite,
    )

    with TestClient(serveur):
        assert fabrique_coordinateur_reclassement().capacite == capacite