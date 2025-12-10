import uvicorn
from adaptateurs.chiffrement import fabrique_adaptateur_chiffrement
from configuration import recupere_configuration
from infra.chiffrement.chiffrement import (
    ServiceDeChiffrement,
    FournisseurDeServiceDeChiffrement,
)
from serveur import fabrique_serveur

configuration = recupere_configuration()
adaptateur_chiffrement = fabrique_adaptateur_chiffrement()
serveur = fabrique_serveur(
    configuration.max_requetes_par_minute, configuration.mode, adaptateur_chiffrement
)


class ServiceDeChiffrementDeTest(ServiceDeChiffrement):
    def dechiffre(self, contenu_chiffre: str) -> str:
        return contenu_chiffre.removesuffix("_chiffre")

    def chiffre(self, contenu: str) -> str:
        return f"{contenu}_chiffre"  # type: ignore


FournisseurDeServiceDeChiffrement.service = ServiceDeChiffrementDeTest()

if __name__ == "__main__":
    HOST = configuration.hote
    PORT = configuration.port
    uvicorn.run(
        "main:serveur",
        host=HOST,
        port=PORT,
        reload=True,
    )
