from typing import Callable

import pytest

from configuration import Albert


@pytest.fixture()
def une_configuration_de_service_albert() -> Callable[[], Albert.Service]:  # type:ignore[attr-defined, name-defined]
    def _une_configuration_de_service_albert() -> Albert.Service:  # type:ignore[attr-defined, name-defined]
        return Albert.Service(  # type:ignore[attr-defined, name-defined]
            collection_nom_anssi_lab="",
            collection_id_anssi_lab=42,
            reclassement_active=False,
            modele_reclassement="Aucun",
            taille_fenetre_historique=10,
            reformulateur_active=True,
        )

    return _une_configuration_de_service_albert
