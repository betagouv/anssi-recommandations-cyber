import pytest
from schemas.violations import (
    ViolationThematique,
    ViolationMalveillance,
    ViolationIdentite,
    Violation,
)


@pytest.mark.parametrize(
    "violation, reponse_attendue",
    [
        (
            ViolationThematique(),
            "Cette thématique n’entre pas dans le cadre de mes compétences et des sources disponibles. Reformulez votre question autour d’un enjeu cybersécurité ou informatique.",
        ),
        (
            ViolationMalveillance(),
            "Désolé, nous n’avons pu générer aucune réponse correspondant à votre question.",
        ),
        (
            ViolationIdentite(),
            "Je suis un service développé par ou pour l’ANSSI afin de répondre aux questions en cybersécurité et informatique, en m’appuyant sur les guides officiels disponibles sur le site de l’agence.",
        ),
    ],
)
def test_serialise_la_violation(violation, reponse_attendue):
    resultat = violation.model_dump()

    assert resultat["reponse"] == reponse_attendue


@pytest.mark.parametrize(
    "violation, violation_attendue",
    [
        (
            "Cette thématique n’entre pas dans le cadre de mes compétences et des sources disponibles. Reformulez votre question autour d’un enjeu cybersécurité ou informatique.",
            ViolationThematique(),
        ),
        (
            "Désolé, nous n’avons pu générer aucune réponse correspondant à votre question.",
            ViolationMalveillance(),
        ),
        (
            "Je suis un service développé par ou pour l’ANSSI afin de répondre aux questions en cybersécurité et informatique, en m’appuyant sur les guides officiels disponibles sur le site de l’agence.",
            ViolationIdentite(),
        ),
    ],
)
def test_deserialise_la_violation(violation, violation_attendue):
    resultat = Violation.model_validate(violation)

    assert resultat == violation_attendue
