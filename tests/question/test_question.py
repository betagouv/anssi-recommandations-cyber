from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.journal import AdaptateurJournalMemoire
from question.question import (
    pose_question_utilisateur,
    ConfigurationQuestion,
    ResultatInteractionEnErreur,
)
from schemas.type_utilisateur import TypeUtilisateur
from serveur_de_test import ServiceAlbertMemoire


def test_pose_question_retourne_un_resultat_d_interaction_en_erreur(
    un_adaptateur_de_chiffrement,
):
    service_albert = ServiceAlbertMemoire()
    service_albert.qui_leve_une_erreur_sur_pose_question()
    reponse = pose_question_utilisateur(
        ConfigurationQuestion(
            adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
            adaptateur_base_de_donnees=AdaptateurBaseDeDonneesEnMemoire(),
            adaptateur_journal=AdaptateurJournalMemoire(),
            service_albert=service_albert,
        ),
        "une question",
        TypeUtilisateur.EXPERT_SSI,
    )

    assert isinstance(reponse, ResultatInteractionEnErreur)
    assert reponse.message_mqc == "Erreur lors de l’appel à Albert"
    assert reponse.erreur == "Erreur sur pose_question"
