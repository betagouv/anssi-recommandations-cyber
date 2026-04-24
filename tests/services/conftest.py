from typing import Callable

import pytest

from configuration import Albert
from schemas.albert import Paragraphe, RechercheMetadonnees


@pytest.fixture()
def une_configuration_de_service_albert() -> Callable[[], Albert.Service]:  # type:ignore[attr-defined, name-defined]
    def _une_configuration_de_service_albert() -> Albert.Service:  # type:ignore[attr-defined, name-defined]
        return Albert.Service(  # type:ignore[attr-defined, name-defined]
            collection_nom_anssi_lab="",
            collection_id_anssi_lab=42,
            collection_id_anssi_lab_jeopardy=43,
            reclassement_active=False,
            modele_reclassement="Aucun",
            taille_fenetre_historique=10,
            jeopardy_active=False,
        )

    return _une_configuration_de_service_albert


@pytest.fixture()
def un_paragraphe_depuis_metadata() -> Callable[..., Paragraphe]:
    def _un_paragraphe_depuis_metadata(
        contenu: str,
        reponse_metadata: str = "",
        score_similarite: float = 0.5,
        score_reclassement: float = 0.5,
    ) -> Paragraphe:
        metadata = RechercheMetadonnees(
            source_url="https://example.com",
            page=0,
            nom_document="faq_reponses_maitrisees",
            reponse=reponse_metadata,
        )
        return Paragraphe(
            contenu=contenu,
            reponse=metadata.reponse,
            score_similarite=score_similarite,
            score_reclassement=score_reclassement,
            numero_page=metadata.page,
            url=metadata.source_url,
            nom_document=metadata.nom_document,
        )

    return _un_paragraphe_depuis_metadata
