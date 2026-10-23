import pytest
from fastapi.testclient import TestClient

from configuration import CapaciteReclassementParallele, Mode
from serveur import fabrique_serveur
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
    ErreurSaturationReclassement,
)


def test_serveur_possede_et_ferme_le_coordinateur_dans_son_cycle_de_vie(
    pages_statiques,
) -> None:
    serveur = fabrique_serveur(600, Mode.TEST, f"{pages_statiques}/ui/dist/")

    with TestClient(serveur):
        coordinateur = serveur.state.coordinateur_reclassement
        assert isinstance(coordinateur, CoordinateurReclassementParallele)

    with pytest.raises(ErreurSaturationReclassement):
        coordinateur.ouvre_workflow()


def test_le_coordinateur_du_serveur_utilise_la_capacite_demandee(
    pages_statiques,
) -> None:
    capacite = CapaciteReclassementParallele(nombre_maximum_d_appels_par_workflow=8)
    serveur = fabrique_serveur(
        600,
        Mode.TEST,
        f"{pages_statiques}/ui/dist/",
        capacite_reclassement=capacite,
    )

    with TestClient(serveur):
        assert serveur.state.coordinateur_reclassement.capacite == capacite
