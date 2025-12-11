import base64
import os
from abc import abstractmethod, ABCMeta

import dpath
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Callable


class ServiceDeChiffrement(metaclass=ABCMeta):
    @abstractmethod
    def chiffre(self, contenu: str) -> str: ...

    @abstractmethod
    def dechiffre(self, contenu_chiffre: str) -> str:
        pass

    def chiffre_dict(self, dictionnaire: dict, clefs: list[str]) -> dict:
        return self.__applique(clefs, self.chiffre, dictionnaire)

    def dechiffre_dict(self, dictionnaire: dict, chemins: list[str]) -> dict:
        return self.__applique(chemins, self.dechiffre, dictionnaire)

    @staticmethod
    def __applique(
        chemins: list[str], fonction: Callable[[str], str], dictionnaire: dict
    ) -> dict:
        dictionnaire_chiffre = dictionnaire
        for chemin in chemins:
            for recherche in dpath.search(dictionnaire, chemin, yielded=True):
                dpath.set(dictionnaire_chiffre, recherche[0], fonction(recherche[1]))
        return dictionnaire_chiffre


class FournisseurDeServiceDeChiffrement:
    service: ServiceDeChiffrement


class ServiceDeChiffrementAES(ServiceDeChiffrement):
    def __init__(self, clef: bytes):
        super().__init__()
        self.clef = clef

    def chiffre(self, contenu: str) -> str:
        aesgcm = AESGCM(self.clef)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, contenu.encode("utf-8"), None)
        return base64.b64encode(nonce).decode("utf-8") + base64.b64encode(
            ciphertext
        ).decode("utf-8")

    def dechiffre(self, contenu_chiffre: str) -> str:
        aesgcm = AESGCM(self.clef)
        nonce = base64.b64decode(contenu_chiffre[:16])
        ciphertext = base64.b64decode(contenu_chiffre[16:])
        return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
