from typing import Optional

from infra.chiffrement.chiffrement import ServiceDeChiffrement


class ServiceDeChiffrementDeTest(ServiceDeChiffrement):
    def __init__(self):
        super().__init__()
        self.chaine_en_clair = None
        self.leve_une_erreur = None
        self.passages = {}

    def chiffre(self, contenu: str) -> str:
        return f"{contenu}_chiffre"

    def dechiffre(self, contenu_chiffre: str, clef: Optional[str] = None) -> str:
        if clef is not None:
            if clef not in self.passages:
                self.passages[clef] = []
            self.passages[clef].append(contenu_chiffre)
        if self.leve_une_erreur is not None:
            raise Exception(self.leve_une_erreur)
        if self.chaine_en_clair is None:
            return contenu_chiffre.removesuffix("_chiffre")
        return self.chaine_en_clair

    def qui_dechiffre(self, chaine_chiffree: str):
        self.chaine_en_clair = chaine_chiffree
        return self

    def qui_leve_une_erreur_au_dechiffrement(self):
        self.leve_une_erreur = "Déchiffrement en erreur"
        return self
