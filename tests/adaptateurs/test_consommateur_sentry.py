from adaptateurs.bus_evenements import BusEvenementsEnMemoire, ErreurTechniqueSurvenue
from adaptateurs.consommateur_sentry import (
    ConsommateurSentry,
    enregistre_consommateur_sentry,
)
from adaptateurs.sentry import AdaptateurSentryMemoire


def test_transmet_l_exception_de_l_evenement_a_l_adaptateur_sentry():
    adaptateur_sentry = AdaptateurSentryMemoire()
    consommateur = ConsommateurSentry(adaptateur_sentry)
    exception = RuntimeError("panne technique")

    consommateur.sur_erreur_technique(
        ErreurTechniqueSurvenue(exception=exception, contexte="génération")
    )

    assert adaptateur_sentry.exceptions_capturees == [exception]


def test_enregistre_capture_les_erreurs_techniques_publiees_sur_le_bus():
    adaptateur_sentry = AdaptateurSentryMemoire()
    bus = BusEvenementsEnMemoire()
    enregistre_consommateur_sentry(bus, adaptateur_sentry)
    exception = RuntimeError("panne technique")

    bus.publie(ErreurTechniqueSurvenue(exception=exception, contexte="reformulation"))

    assert adaptateur_sentry.exceptions_capturees == [exception]