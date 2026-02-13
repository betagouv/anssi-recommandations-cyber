import uuid

from typing import Union, NamedTuple

from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.chiffrement import AdaptateurChiffrement

from adaptateurs.journal import (
    TypeEvenement,
    DonneesInteractionCreee,
    DonneesViolationDetectee,
    AdaptateurJournal,
)
from conversation.conversation import (
    QuestionUtilisateur,
    ResultatConversation,
    ResultatInteractionEnErreur,
    Conversation,
    Interaction,
)
from schemas.albert import ReponseQuestion
from schemas.type_utilisateur import TypeUtilisateur
from services.service_albert import ServiceAlbert


class ConfigurationQuestion(NamedTuple):
    service_albert: ServiceAlbert
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees
    adaptateur_journal: AdaptateurJournal
    adaptateur_chiffrement: AdaptateurChiffrement


def pose_question_utilisateur(
    configuration: ConfigurationQuestion,
    question_utilisateur: QuestionUtilisateur,
    type_utilisateur: TypeUtilisateur,
) -> Union[ResultatConversation, ResultatInteractionEnErreur]:
    try:
        conversation = None
        if question_utilisateur.conversation is not None:
            conversation = (
                configuration.adaptateur_base_de_donnees.recupere_conversation(
                    question_utilisateur.conversation
                )
            )
        reponse_question = configuration.service_albert.pose_question(
            question=question_utilisateur.question, conversation=conversation
        )
        interaction, reponse_question = __cree_interaction(
            question_utilisateur, reponse_question
        )
        if conversation is not None:
            conversation.ajoute_interaction(interaction)
        else:
            conversation = Conversation(interaction)
        configuration.adaptateur_base_de_donnees.sauvegarde_conversation(conversation)
        id_interaction = str(interaction.id)
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
        return ResultatConversation(
            conversation.id_conversation, reponse_question, interaction, id_interaction
        )
    except Exception as e:
        return ResultatInteractionEnErreur(e)


def __cree_interaction(
    question_utilisateur: QuestionUtilisateur, reponse_question: ReponseQuestion
) -> tuple[Interaction, ReponseQuestion]:
    if reponse_question.violation is not None:
        reponse_question = ReponseQuestion(
            reponse=reponse_question.violation.reponse,
            paragraphes=[],
            question=(question_utilisateur.question),
            violation=reponse_question.violation,
        )
    interaction = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
    )
    return interaction, reponse_question
