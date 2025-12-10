import base64
import os
from abc import abstractmethod, ABCMeta
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class ServiceDeChiffrement(metaclass=ABCMeta):
    @abstractmethod
    def chiffre(self, contenu: str) -> str: ...

    @abstractmethod
    def dechiffre(self, contenu_chiffre: str) -> str:
        pass


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
