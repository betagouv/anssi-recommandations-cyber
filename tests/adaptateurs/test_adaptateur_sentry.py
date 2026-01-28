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


def test_capture_message_stocke_le_message():
    adaptateur_sentry = AdaptateurSentryMemoire()
    message = "Message de test"

    adaptateur_sentry.capture_message(message)

    assert len(adaptateur_sentry.messages_captures) == 1
    assert adaptateur_sentry.messages_captures[0] == message


def test_definis_contexte_stocke_le_contexte():
    adaptateur_sentry = AdaptateurSentryMemoire()

    adaptateur_sentry.definis_contexte("interaction", {"id": "123", "question": "test"})

    assert "interaction" in adaptateur_sentry.contextes
    assert adaptateur_sentry.contextes["interaction"]["id"] == "123"
