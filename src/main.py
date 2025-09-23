import uvicorn
from configuration import recupere_configuration
from serveur import fabrique_serveur

configuration = recupere_configuration()
serveur = fabrique_serveur(configuration.mode)

if __name__ == "__main__":
    HOST = configuration.host
    PORT = configuration.port
    uvicorn.run(
        "main:serveur",
        host=HOST,
        port=PORT,
        reload=True,
    )
