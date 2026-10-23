from typing import Any, cast

import pytest

from adaptateurs.bus_evenements import (
    BusEvenementsEnMemoire,
    ErreurTechniqueSurvenue,
)
from classification_de_test import (
    classification_element_de_reponse,
    classification_preuve_principale,
    reponse_classification_avec_identifiants_globaux,
)
from reclassement_llm_support import un_reclasseur_qui_repond
from schemas.albert import ParagrapheReponseMaitrisee
from services.contrat_reclassement_llm import schema_classification
from services.exceptions import ErreurCommunicationModeleReclassement
from unites_source_de_test import une_table_des_matieres, une_unite_source


def reponse_sans_preuve_pour(identifiants) -> str:
    return reponse_classification_avec_identifiants_globaux(
        {
            identifiant: classification_element_de_reponse()
            for identifiant in identifiants
        }
    )


def test_ne_contacte_pas_le_modele_sans_candidat() -> None:
    reclasseur, client = un_reclasseur_qui_repond()

    resultat = reclasseur.reclasse("Une question ?", [])

    assert resultat.paragraphes_retenus == []
    assert resultat.aucune_source_utile is True
    assert client.messages_envoyes_pour_les_propositions == []


def test_classifie_les_lots_sequentiellement_avec_leur_schema(des_paragraphes) -> None:
    reclasseur, client = un_reclasseur_qui_repond(
        reponse_sans_preuve_pour(range(1, 6)), reponse_sans_preuve_pour([6])
    )
    paragraphes = des_paragraphes(6)

    resultat = reclasseur.reclasse("Une question ?", paragraphes)

    formats = [cast(Any, f)["json_schema"] for f in client.formats_reponse_recus]
    assert resultat.tous_les_candidats == paragraphes
    assert [f["name"] for f in formats] == ["classification_passages"] * 2
    assert all(f["strict"] is True for f in formats)
    assert [f["schema"] for f in formats] == [
        schema_classification(paragraphes[:5], premier_id=1),
        schema_classification(paragraphes[5:], premier_id=6),
    ]
    assert client.temperatures_recues == [0, 0]


def test_le_prompt_presente_chaque_candidat_avec_ses_unites(
    un_constructeur_de_paragraphe,
) -> None:
    paragraphe = (
        un_constructeur_de_paragraphe()
        .avec_les_unites_source(
            [
                une_unite_source("Première unité", numero_page=3),
                une_table_des_matieres("Sommaire", numero_page=3),
            ]
        )
        .construis()
    )
    reclasseur, client = un_reclasseur_qui_repond(
        reponse_sans_preuve_pour([1]),
        prompt_classification="{QUESTION}\n{CANDIDATS}",
    )

    reclasseur.reclasse("Une question ?", [paragraphe])

    prompt = str(
        cast(Any, client.messages_envoyes_pour_les_propositions[0][0])["content"]
    )
    assert prompt.startswith("Une question ?\n[PASSAGE id=1 ")
    assert "[UNITE id=1 page=3 type_de_bloc='paragraphe'" in prompt
    assert "[UNITE id=2 page=3 type_de_bloc='table_des_matieres'" in prompt
    assert "Première unité" in prompt


@pytest.mark.parametrize(
    "classification",
    [
        pytest.param(classification_element_de_reponse(), id="element_de_reponse"),
        pytest.param(
            classification_element_de_reponse(
                relation="indirecte", apport="reponse_centrale"
            ),
            id="complement_indirect",
        ),
    ],
)
def test_ne_retient_aucun_paragraphe_sans_preuve_principale(
    des_paragraphes, classification
) -> None:
    reclasseur, _ = un_reclasseur_qui_repond(
        reponse_classification_avec_identifiants_globaux({1: classification})
    )
    candidats = des_paragraphes(1)

    resultat = reclasseur.reclasse("Une question ?", candidats)

    assert resultat.paragraphes_retenus == []
    assert resultat.tous_les_candidats == candidats
    assert resultat.aucune_source_utile is True


def test_ne_reclasse_aucun_candidat_sans_preuve_de_portee_admissible(
    des_paragraphes,
) -> None:
    reclasseur, _ = un_reclasseur_qui_repond(
        reponse_classification_avec_identifiants_globaux(
            {
                1: classification_preuve_principale(
                    portee="specifique_non_demandee", apport="reponse_centrale"
                ),
                2: classification_element_de_reponse(),
            }
        )
    )
    candidats = des_paragraphes(2)

    resultat = reclasseur.reclasse("Une question ?", candidats)

    assert resultat.paragraphes_retenus == []
    assert resultat.tous_les_candidats == candidats
    assert resultat.aucune_source_utile is True


def test_fusionne_les_preuves_et_conserve_les_candidats_originaux(
    un_constructeur_de_paragraphe_reponse_maitrisee,
) -> None:
    reclasseur, _ = un_reclasseur_qui_repond(
        reponse_classification_avec_identifiants_globaux(
            {1: classification_preuve_principale()}
        )
    )
    paragraphe = un_constructeur_de_paragraphe_reponse_maitrisee().construis()

    resultat = reclasseur.reclasse("Une question ?", [paragraphe])

    retenu = resultat.paragraphes_retenus[0]
    assert retenu.contenu == paragraphe.contenu
    assert retenu.score_reclassement == 1.0
    assert isinstance(retenu, ParagrapheReponseMaitrisee)
    assert resultat.tous_les_candidats == [paragraphe]


def test_cite_la_page_de_l_unite_probante_designee_par_le_modele(
    un_constructeur_de_paragraphe,
) -> None:
    paragraphe = (
        un_constructeur_de_paragraphe()
        .a_la_page(33)
        .avec_les_unites_source(
            [une_unite_source(numero_page=page) for page in (33, 34, 35)]
        )
        .construis()
    )
    reclasseur, _ = un_reclasseur_qui_repond(
        reponse_classification_avec_identifiants_globaux(
            {1: classification_preuve_principale(unite_probante=3)}
        )
    )

    resultat = reclasseur.reclasse("Une question ?", [paragraphe])

    assert [p.numero_page for p in resultat.paragraphes_retenus] == [35]


def test_reunit_toutes_les_preuves_du_degre_maximal_sur_tous_les_lots(
    des_paragraphes,
) -> None:
    def reponse_pour(identifiants: range) -> str:
        return reponse_classification_avec_identifiants_globaux(
            {
                identifiant: classification_preuve_principale(
                    apport="reponse_centrale"
                    if identifiant <= 8
                    else "explication_directe"
                )
                for identifiant in identifiants
            }
        )

    reclasseur, client = un_reclasseur_qui_repond(
        reponse_pour(range(1, 6)),
        reponse_pour(range(6, 11)),
        reponse_pour(range(11, 13)),
    )

    resultat = reclasseur.reclasse("Une question ?", des_paragraphes(12))

    assert [p.contenu for p in resultat.paragraphes_retenus] == [
        f"Passage {identifiant}" for identifiant in range(1, 9)
    ]
    assert len(client.messages_envoyes_pour_les_propositions) == 3


def test_une_reponse_inexploitable_est_signalee_comme_une_erreur_technique(
    des_paragraphes,
) -> None:
    bus = BusEvenementsEnMemoire()
    erreurs: list[ErreurTechniqueSurvenue] = []
    bus.souscris(ErreurTechniqueSurvenue, erreurs.append)
    reclasseur, _ = un_reclasseur_qui_repond("pas du json", bus=bus)

    with pytest.raises(ErreurCommunicationModeleReclassement) as erreur:
        reclasseur.reclasse("Une question ?", des_paragraphes(1))

    assert isinstance(erreur.value.__cause__, ValueError)
    assert len(erreurs) == 1
