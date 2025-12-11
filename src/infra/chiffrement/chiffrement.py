import base64
import copy
from abc import abstractmethod, ABCMeta
import secrets
import dpath
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class ServiceDeChiffrement(metaclass=ABCMeta):
    @abstractmethod
    def chiffre(self, contenu: str) -> str: ...

    @abstractmethod
    def dechiffre(self, contenu_chiffre: str) -> str:
        pass

    def chiffre_dict(
        self, dictionnaire: dict, chemins_a_conserver_en_clair: list[str]
    ) -> dict:
        dictionnaire_chiffre = copy.deepcopy(dictionnaire)

        self.__chiffre_tout(dictionnaire_chiffre)

        for clef in chemins_a_conserver_en_clair:
            for recherche in dpath.search(dictionnaire, clef, yielded=True):
                dpath.set(dictionnaire_chiffre, recherche[0], recherche[1])
        return dictionnaire_chiffre

    def __chiffre_tout(self, dictionnaire_chiffre: dict) -> None:
        for clef, valeur in dictionnaire_chiffre.items():
            match valeur:
                case str():
                    dictionnaire_chiffre[clef] = self.chiffre(valeur)
                case dict():
                    self.__chiffre_tout(valeur)
                case list():
                    for i, element in enumerate(valeur):
                        match element:
                            case str():
                                valeur[i] = self.chiffre(element)
                            case dict():
                                self.__chiffre_tout(element)


class FournisseurDeServiceDeChiffrement:
    service: ServiceDeChiffrement


class ServiceDeChiffrementAES(ServiceDeChiffrement):
    def __init__(self, clef: bytes):
        super().__init__()
        self.clef = clef

    def chiffre(self, contenu: str) -> str:
        aesgcm = AESGCM(self.clef)
        nonce = secrets.token_bytes(12)
        ciphertext = aesgcm.encrypt(nonce, contenu.encode("utf-8"), None)
        return base64.b64encode(nonce).decode("utf-8") + base64.b64encode(
            ciphertext
        ).decode("utf-8")

    def dechiffre(self, contenu_chiffre: str) -> str:
        aesgcm = AESGCM(self.clef)
        nonce = base64.b64decode(contenu_chiffre[:16])
        ciphertext = base64.b64decode(contenu_chiffre[16:])
        return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
