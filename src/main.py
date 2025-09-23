import uvicorn
from configuration import recupere_configuration
from serveur import app

if __name__ == "__main__":
    configuration = recupere_configuration()
    HOST = configuration.host
    PORT = configuration.port
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
    )
