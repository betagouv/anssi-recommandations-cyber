import uvicorn

from adaptateurs.chiffrement import fabrique_adaptateur_chiffrement
from configuration import recupere_configuration
from infra.chiffrement.chiffrement import (
    fabrique_fournisseur_de_chiffrement,
)
from serveur import fabrique_serveur

configuration = recupere_configuration()
adaptateur_chiffrement = fabrique_adaptateur_chiffrement()
serveur = fabrique_serveur(configuration.max_requetes_par_minute, configuration.mode)
fabrique_fournisseur_de_chiffrement(configuration)

if __name__ == "__main__":
    HOST = configuration.hote
    PORT = configuration.port
    uvicorn.run(
        "main:serveur",
        host=HOST,
        port=PORT,
        reload=True,
    )
