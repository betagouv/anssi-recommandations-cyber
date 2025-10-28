import uvicorn
from adaptateurs.chiffrement import fabrique_adaptateur_chiffrement
from configuration import recupere_configuration
from serveur import fabrique_serveur

configuration = recupere_configuration()
adaptateur_chiffrement = fabrique_adaptateur_chiffrement()
serveur = fabrique_serveur(configuration.mode, adaptateur_chiffrement)

if __name__ == "__main__":
    HOST = configuration.hote
    PORT = configuration.port
    uvicorn.run(
        "main:serveur",
        host=HOST,
        port=PORT,
        reload=True,
    )
