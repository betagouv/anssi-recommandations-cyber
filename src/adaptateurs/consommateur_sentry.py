from adaptateurs.bus_evenements import BusEvenements, ErreurTechniqueSurvenue
from adaptateurs.sentry import AdaptateurSentry


class ConsommateurSentry:
    def __init__(self, adaptateur_sentry: AdaptateurSentry) -> None:
        self.adaptateur_sentry = adaptateur_sentry

    def sur_erreur_technique(self, evenement: ErreurTechniqueSurvenue) -> None:
        self.adaptateur_sentry.capture_exception(evenement.exception)


def enregistre_consommateur_sentry(
    bus_evenements: BusEvenements, adaptateur_sentry: AdaptateurSentry
) -> ConsommateurSentry:
    consommateur = ConsommateurSentry(adaptateur_sentry)
    bus_evenements.souscris(ErreurTechniqueSurvenue, consommateur.sur_erreur_technique)
    return consommateur