import functools
from abc import abstractmethod, ABCMeta
from typing import Any


class ServiceDeChiffrement(metaclass=ABCMeta):
    @abstractmethod
    def chiffre(self, contenu: str) -> str: ...

    @abstractmethod
    def dechiffre(self, contenu_chiffre: str) -> str:
        pass


class FournisseurDeServiceDeChiffrement:
    service: ServiceDeChiffrement


def chiffre(modele: dict):
    def fonction_de_chiffrement(func) -> Any:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            resultat = func(*args, **kwargs)
            for cle in modele["cles"]:
                contenu_chiffre = FournisseurDeServiceDeChiffrement.service.chiffre(
                    contenu=resultat[cle]
                )
                resultat[cle] = f"{contenu_chiffre.decode('utf-8')}"
            return resultat

        return wrapper

    return fonction_de_chiffrement
