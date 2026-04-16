import logging

import uvicorn

from adaptateurs.chiffrement import fabrique_adaptateur_chiffrement
from configuration import recupere_configuration
from infra.logger import log
from serveur import fabrique_serveur

try:
    configuration = recupere_configuration()
except Exception as e:
    logging.error(e)
    exit(1)

adaptateur_chiffrement = fabrique_adaptateur_chiffrement()
serveur = fabrique_serveur(configuration.max_requetes_par_minute, configuration.mode)

log(
    __name__,
    f"ℹ️ Configuration Albert :\n"
    f"  Modèle : {configuration.albert.client.modele_reponse}\n"
    f"  Reclassement actif : {'Oui' if configuration.albert.service.reclassement_active else 'Non'} - Modèle {configuration.albert.service.modele_reclassement}\n"
    f"  Identifiant collection ANSSI : {configuration.albert.service.collection_id_anssi_lab}\n"
    f"  Recherche hybride : {'Oui' if configuration.albert.client.utilise_recherche_hybride else 'Non'}\n",
)

if __name__ == "__main__":
    HOST = configuration.hote
    PORT = configuration.port
    uvicorn.run(
        "main:serveur",
        host=HOST,
        port=PORT,
        reload=True,
    )
