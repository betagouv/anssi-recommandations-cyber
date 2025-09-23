import uvicorn
from configuration import recupere_configuration
from serveur import fabrique_serveur

serveur = fabrique_serveur()

if __name__ == "__main__":
    configuration = recupere_configuration()
    HOST = configuration.host
    PORT = configuration.port
    uvicorn.run(
        "main:serveur",
        host=HOST,
        port=PORT,
        reload=True,
    )
