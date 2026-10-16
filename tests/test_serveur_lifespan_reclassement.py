import pytest
from fastapi.testclient import TestClient

from configuration import Mode, calcule_capacite_reclassement_parallele
from serveur import fabrique_serveur
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
    ErreurSaturationReclassement,
)


def test_serveur_possede_et_ferme_le_coordinateur_dans_son_lifespan(
    pages_statiques,
) -> None:
    serveur = fabrique_serveur(600, Mode.TEST, f"{pages_statiques}/ui/dist/")

    with TestClient(serveur):
        coordinateur = serveur.state.coordinateur_reclassement
        assert isinstance(coordinateur, CoordinateurReclassementParallele)

    with pytest.raises(ErreurSaturationReclassement):
        serveur.state.coordinateur_reclassement.ouvre_workflow()


def test_lifespan_utilise_la_capacite_derivee_des_collections_et_des_lots(
    pages_statiques,
) -> None:
    capacite = calcule_capacite_reclassement_parallele(20, 5, True)
    serveur = fabrique_serveur(
        600,
        Mode.TEST,
        f"{pages_statiques}/ui/dist/",
        capacite_reclassement=capacite,
    )

    with TestClient(serveur):
        coordinateur = serveur.state.coordinateur_reclassement
        assert coordinateur.nombre_maximum_de_candidats == 40
        assert coordinateur.nombre_maximum_d_appels_par_workflow == 8
        assert coordinateur.nombre_maximum_de_workflows == 2
