import uuid
from typing import NamedTuple, Union

from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.chiffrement import AdaptateurChiffrement
from adaptateurs.journal import (
    TypeEvenement,
    DonneesInteractionCreee,
    DonneesViolationDetectee,
    AdaptateurJournal,
)
from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import Interaction
from schemas.type_utilisateur import TypeUtilisateur
from services.service_albert import ServiceAlbert


class ConfigurationQuestion(NamedTuple):
    service_albert: ServiceAlbert
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees
    adaptateur_journal: AdaptateurJournal
    adaptateur_chiffrement: AdaptateurChiffrement


class ResultatInteraction:
    def __init__(
        self,
        id_interaction: str,
        reponse_question: ReponseQuestion,
        interaction: Interaction,
    ):
        self.id_interaction = id_interaction
        self.reponse_question = reponse_question
        self.interaction = interaction


class ResultatInteractionEnErreur:
    def __init__(self, e: Exception):
        self.message_mqc = "Erreur lors de l’appel à Albert"
        self.erreur = str(e)


def pose_question_utilisateur(
    configuration: ConfigurationQuestion,
    question: str,
    type_utilisateur: TypeUtilisateur,
) -> Union[ResultatInteraction, ResultatInteractionEnErreur]:
    try:
        reponse_question = configuration.service_albert.pose_question(question)
        interaction = Interaction(
            reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
        )
        id_interaction = str(interaction.id)
        (configuration.adaptateur_base_de_donnees.sauvegarde_interaction(interaction))
        configuration.adaptateur_journal.consigne_evenement(
            type=TypeEvenement.INTERACTION_CREEE,
            donnees=DonneesInteractionCreee(
                id_interaction=configuration.adaptateur_chiffrement.hache(
                    id_interaction
                ),
                longueur_question=len(reponse_question.question.strip()),
                longueur_reponse=len(reponse_question.reponse.strip()),
                longueur_paragraphes=sum(
                    (list(map(lambda r: len(r.contenu), reponse_question.paragraphes)))
                ),
                type_utilisateur=type_utilisateur,
            ),
        )

        if reponse_question.violation is not None:
            configuration.adaptateur_journal.consigne_evenement(
                type=TypeEvenement.VIOLATION_DETECTEE,
                donnees=DonneesViolationDetectee(
                    id_interaction=configuration.adaptateur_chiffrement.hache(
                        id_interaction
                    ),
                    type_violation=reponse_question.violation.__class__.__name__,
                ),
            )
        return ResultatInteraction(id_interaction, reponse_question, interaction)
    except Exception as e:
        return ResultatInteractionEnErreur(e)
