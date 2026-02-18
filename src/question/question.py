import uuid
from uuid import UUID

from typing import NamedTuple, Union

from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.chiffrement import AdaptateurChiffrement
from adaptateurs.journal import (
    TypeEvenement,
    DonneesInteractionCreee,
    DonneesViolationDetectee,
    AdaptateurJournal,
    DonneesConversationCreee,
)
from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import (
    Interaction,
    RetourUtilisatrice,
    DonneesCreationRetourUtilisateur,
    Conversation,
    TagPositif,
    TagNegatif,
)
from schemas.type_utilisateur import TypeUtilisateur
from services.service_albert import ServiceAlbert


class ConfigurationQuestion(NamedTuple):
    service_albert: ServiceAlbert
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees
    adaptateur_journal: AdaptateurJournal
    adaptateur_chiffrement: AdaptateurChiffrement


class ResultatConversation:
    def __init__(
        self,
        id_conversation: uuid.UUID,
        reponse_question: ReponseQuestion,
        interaction: Interaction,
        id_interaction: str,
    ):
        self.id_interaction = id_interaction
        self.reponse_question = reponse_question
        self.interaction = interaction
        self.id_conversation = id_conversation


class ResultatConversationEnErreur:
    def __init__(self, e: Exception):
        self.message_mqc = "Erreur lors de l’appel à Albert"
        self.erreur = str(e)


class ResultatConversationInconnue:
    def __init__(self):
        self.message_mqc = "La conversation demandée n'existe pas"


class DemandeConversationUtilisateur(NamedTuple):
    question: str


class DemandeInteractionUtilisateur(NamedTuple):
    question: str
    conversation: uuid.UUID


def cree_conversation(
    configuration: ConfigurationQuestion,
    question_utilisateur: DemandeConversationUtilisateur,
    type_utilisateur: TypeUtilisateur,
) -> Union[ResultatConversation, ResultatConversationEnErreur]:
    try:
        reponse_question = configuration.service_albert.pose_question(
            question=question_utilisateur.question
        )
        interaction, reponse_question = __cree_interaction(
            question_utilisateur.question, reponse_question
        )
        conversation = Conversation(interaction)
        configuration.adaptateur_base_de_donnees.sauvegarde_conversation(conversation)
        id_interaction = str(interaction.id)
        configuration.adaptateur_journal.consigne_evenement(
            type=TypeEvenement.CONVERSATION_CREEE,
            donnees=DonneesConversationCreee(
                id_conversation=configuration.adaptateur_chiffrement.hache(
                    str(conversation.id_conversation)
                ),
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
        return ResultatConversationEnErreur(e)


def ajoute_interaction(
    configuration: ConfigurationQuestion,
    question_utilisateur: DemandeInteractionUtilisateur,
    type_utilisateur: TypeUtilisateur,
) -> Union[
    ResultatConversation, ResultatConversationEnErreur, ResultatConversationInconnue
]:
    try:
        conversation = configuration.adaptateur_base_de_donnees.recupere_conversation(
            question_utilisateur.conversation
        )
        if conversation is None:
            return ResultatConversationInconnue()
        reponse_question = configuration.service_albert.pose_question(
            question=question_utilisateur.question, conversation=conversation
        )
        interaction, reponse_question = __cree_interaction(
            question_utilisateur.question, reponse_question
        )
        conversation.ajoute_interaction(interaction)
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
        return ResultatConversationEnErreur(e)


def __cree_interaction(
    question: str,
    reponse_question: ReponseQuestion,
) -> tuple[Interaction, ReponseQuestion]:
    if reponse_question.violation is not None:
        reponse_question = ReponseQuestion(
            reponse=reponse_question.violation.reponse,
            paragraphes=[],
            question=(question),
            violation=reponse_question.violation,
        )
    interaction = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
    )
    return interaction, reponse_question


def ajoute_retour_utilisatrice(
    donnees_ajout_retour: DonneesCreationRetourUtilisateur,
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees,
) -> RetourUtilisatrice | None:
    if donnees_ajout_retour.id_conversation is not None:
        id_conversation = donnees_ajout_retour.id_conversation

        conversation = adaptateur_base_de_donnees.recupere_conversation(
            id_conversation=uuid.UUID(id_conversation)
        )

        interaction = list(
            filter(
                lambda i: str(i.id) == donnees_ajout_retour.id_interaction,
                conversation.interactions,
            )
        )[0]
        retour = donnees_ajout_retour.retour
        if len(conversation.interactions) < 2:
            retour.tags = [
                t
                for t in retour.tags
                if t != TagNegatif.Conversation and t != TagPositif.Conversation
            ]  # type: ignore[assignment]
    else:
        interaction = adaptateur_base_de_donnees.recupere_interaction(
            uuid.UUID(donnees_ajout_retour.id_interaction)
        )
        retour = donnees_ajout_retour.retour

    if not interaction:
        return None

    interaction.retour_utilisatrice = retour
    adaptateur_base_de_donnees.sauvegarde_interaction(interaction)
    return interaction.retour_utilisatrice


def supprime_retour_utilisatrice(
    identifiant_interaction: UUID, adaptateur_base_de_donnees: AdaptateurBaseDeDonnees
) -> None:
    interaction = adaptateur_base_de_donnees.recupere_interaction(
        identifiant_interaction
    )

    if not interaction:
        return None

    interaction.retour_utilisatrice = None
    adaptateur_base_de_donnees.sauvegarde_interaction(interaction)
    return None
