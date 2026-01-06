from fastapi import Depends

from adaptateurs import AdaptateurBaseDeDonnees, AdaptateurBaseDeDonneesPostgres
from adaptateurs.chiffrement import (
    AdaptateurChiffrement,
    fabrique_adaptateur_chiffrement,
)
from configuration import recupere_configuration


def fabrique_adaptateur_base_de_donnees(
    adaptateur_chiffrement: AdaptateurChiffrement = Depends(
        fabrique_adaptateur_chiffrement
    ),
) -> AdaptateurBaseDeDonnees:
    return AdaptateurBaseDeDonneesPostgres(
        recupere_configuration().base_de_donnees.nom,
        adaptateur_chiffrement.service_de_chiffrement,
    )
