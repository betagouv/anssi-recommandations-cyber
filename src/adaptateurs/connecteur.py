from abc import ABC, abstractmethod

import psycopg2

from configuration import BaseDeDonnees


class Connecteur(ABC):
    @abstractmethod
    def cursor(self):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def placeholder(self) -> str:
        pass


class ConnecteurPostgresql(Connecteur):
    def __init__(
        self,
        base_de_donnees: BaseDeDonnees,
    ):
        self._connexion = psycopg2.connect(
            host=base_de_donnees.hote,
            database=base_de_donnees.nom,
            user=base_de_donnees.utilisateur,
            password=base_de_donnees.mot_de_passe,
            port=base_de_donnees.port,
        )

    def cursor(self):
        return self._connexion.cursor()

    def commit(self):
        self._connexion.commit()

    def close(self):
        self._connexion.close()

    def placeholder(self) -> str:
        return "%s"

    def auto_commit(self):
        self._connexion.autocommit = True
