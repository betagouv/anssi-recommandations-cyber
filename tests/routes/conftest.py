import pytest

from adaptateur_chiffrement import ConstructeurAdaptateurChiffrement


@pytest.fixture
def adaptateur_chiffrement():
    return (
        ConstructeurAdaptateurChiffrement()
        .qui_retourne_nonce("un-nonce")
        .qui_hache("test")
        .construis()
    )
