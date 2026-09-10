from adaptateurs.bus_evenements import BusEvenementsEnMemoire, ErreurTechniqueSurvenue
from adaptateurs.sentry import AdaptateurSentryMemoire
from configuration import Mode
from serveur import fabrique_serveur


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