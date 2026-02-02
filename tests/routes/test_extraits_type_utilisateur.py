from serveur import extrais_type_utilisateur
from adaptateur_chiffrement import AdaptateurChiffrementDeTest


def test_extraits_type_utilisateur():
    adaptateur_chiffrement = AdaptateurChiffrementDeTest()
    type_utilisateur = "jOrtest 123=="

    extrais_type_utilisateur(adaptateur_chiffrement, type_utilisateur)

    assert adaptateur_chiffrement.contenu_recu == "jOrtest+123=="
