from adaptateurs.chiffrement import AdaptateurChiffrement
from configuration import Chiffrement
from infra.chiffrement.chiffrement import ServiceDeChiffrementEnClair
from schemas.type_utilisateur import TypeUtilisateur
from service_chiffrement_de_test import ServiceDeChiffrementDeTest


configuration_chiffrement = Chiffrement(clef_chiffrement="", sel_de_hachage="")


class AdaptateurChiffrementDeTest(AdaptateurChiffrement):
    def __init__(self):
        super().__init__(
            configuration=configuration_chiffrement,
            service_de_chiffrement=ServiceDeChiffrementEnClair(),
        )
        self.contenu_recu = None
        self._nonce = None
        self._hache = None
        self.valeur_recue_pour_le_hache = None

    def hache(self, valeur: str) -> str:
        self.valeur_recue_pour_le_hache = valeur
        return self._hache if self._hache is not None else valeur

    def recupere_nonce(self) -> str:
        return self._nonce

    def chiffre(self, contenu: str) -> str:
        return contenu

    def dechiffre(self, contenu_chiffre: str) -> str:
        self.contenu_recu = contenu_chiffre
        return self.service_de_chiffrement.dechiffre(contenu_chiffre)

    def qui_retourne_nonce(self, nonce: str):
        self._nonce = nonce
        return self

    def qui_hache(self, hache: str):
        self._hache = hache
        return self

    def qui_dechiffre(
        self, type_utilisateur: TypeUtilisateur | str
    ) -> AdaptateurChiffrement:
        self.service_de_chiffrement = ServiceDeChiffrementDeTest().qui_dechiffre(
            type_utilisateur
        )
        return self

    def qui_leve_une_erreur_au_dechiffrement(self) -> AdaptateurChiffrement:
        self.service_de_chiffrement = (
            ServiceDeChiffrementDeTest().qui_leve_une_erreur_au_dechiffrement()
        )
        return self
