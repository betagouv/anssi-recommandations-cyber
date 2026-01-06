import pytest

from adaptateur_chiffrement import AdaptateurChiffrementDeTest


@pytest.fixture
def adaptateur_chiffrement():
    return (
        AdaptateurChiffrementDeTest().qui_retourne_nonce("un-nonce").qui_hache("test")
    )
