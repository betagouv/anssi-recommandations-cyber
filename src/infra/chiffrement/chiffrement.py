import base64
import copy
import logging
from abc import abstractmethod, ABCMeta
import secrets
import dpath
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Callable

from configuration import Configuration


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

    def dechiffre_dict(self, dictionnaire: dict, chemins: list[str]) -> dict:
        dictionnaire_chiffre = copy.deepcopy(dictionnaire)

        for chemin in chemins:
            self.__dechiffre_tout(chemin, dictionnaire_chiffre)
        return dictionnaire_chiffre

    def __dechiffre_tout(
        self, chemin: str, dictionnaire_chiffre: dict, chemin_parcouru: str = ""
    ):
        for clef, valeur in dictionnaire_chiffre.items():
            match valeur:
                case str():
                    if clef != chemin or chemin_parcouru == chemin:
                        dpath.set(dictionnaire_chiffre, clef, self.dechiffre(valeur))
                case dict():
                    self.__dechiffre_tout(
                        chemin,
                        valeur,
                        f"{clef}"
                        if chemin_parcouru == ""
                        else f"{chemin_parcouru}/{clef}",
                    )

                case list():
                    for i, element in enumerate(valeur):
                        match element:
                            case str():
                                if f"{chemin_parcouru}/{clef}" != chemin:
                                    dpath.set(
                                        dictionnaire_chiffre,
                                        f"{clef}/{i}",
                                        self.dechiffre(element),
                                    )
                            case dict():
                                self.__dechiffre_tout(chemin, element, f"{clef}/*")

    @staticmethod
    def __applique(
        chemins: list[str], fonction: Callable[[str], str], dictionnaire: dict
    ) -> dict:
        dictionnaire_chiffre = dictionnaire
        for chemin in chemins:
            for recherche in dpath.search(dictionnaire, chemin, yielded=True):
                if recherche[1] is not None:
                    dpath.set(
                        dictionnaire_chiffre, recherche[0], fonction(recherche[1])
                    )
        return dictionnaire_chiffre


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
        try:
            return self.__dechiffre_la_chaine(contenu_chiffre)
        except DechiffrementException as e:
            logging.warn(f"Exception : {e} - contenu : {str(contenu_chiffre)}")  # type: ignore
            return contenu_chiffre

    def __dechiffre_la_chaine(self, contenu_chiffre: str) -> str:
        try:
            aesgcm = AESGCM(self.clef)
            nonce = base64.b64decode(contenu_chiffre[:16])
            ciphertext = base64.b64decode(contenu_chiffre[16:])
            return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as e:
            raise DechiffrementException(str(e))


class DechiffrementException(Exception):
    def __init__(self, message: str):
        super().__init__(f"Erreur de déchiffrement : {message}")


class ServiceDeChiffrementEnClair(ServiceDeChiffrement):
    def dechiffre(self, contenu_chiffre: str) -> str:
        return contenu_chiffre.removesuffix("_chiffre")

    def chiffre(self, contenu: str) -> str:
        return f"{contenu}_chiffre"  # type: ignore


def fabrique_service_de_chiffrement(
    configuration: Configuration,
) -> ServiceDeChiffrement:
    clef_chiffrement = configuration.chiffrement.clef_chiffrement
    if clef_chiffrement is not None:
        return ServiceDeChiffrementAES(clef_chiffrement.encode("utf-8"))

    else:
        return ServiceDeChiffrementEnClair()
