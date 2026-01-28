import os
from unittest.mock import patch
from configuration import recupere_configuration
from adaptateurs.sentry import AdaptateurSentryMemoire


def test_configuration_sentry_avec_variables_environnement():
    with patch.dict(
        os.environ,
        {
            "SENTRY_DSN": "https://test@sentry.io/123",
            "SENTRY_ENVIRONNEMENT": "test",
        },
    ):
        configuration = recupere_configuration()

        assert configuration.sentry.dsn == "https://test@sentry.io/123"
        assert configuration.sentry.environnement == "test"


def test_configuration_sentry_avec_valeurs_par_defaut():
    with patch.dict(os.environ, {}, clear=True):
        configuration = recupere_configuration()

        assert configuration.sentry.dsn is None
        assert configuration.sentry.environnement == "developpement"


def test_capture_exception_stocke_l_exception():
    adaptateur_sentry = AdaptateurSentryMemoire()
    exception = Exception("Erreur de test")

    adaptateur_sentry.capture_exception(exception)

    assert len(adaptateur_sentry.exceptions_capturees) == 1
    assert adaptateur_sentry.exceptions_capturees[0] == exception
