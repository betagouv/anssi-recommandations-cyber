import pytest
from configuration import Albert


@pytest.fixture
def une_configuration_albert_client():
    return Albert.Client(  # type: ignore [attr-defined]
        api_key="",
        base_url="",
        modele_reponse="",
        temps_reponse_maximum_pose_question=10.0,
        temps_reponse_maximum_recherche_paragraphes=1.0,
        utilise_recherche_hybride=False,
        decalage_index_Albert_et_numero_de_page_lecteur=0,
    )
