import uuid
from uuid import UUID

from typing import NamedTuple, Union, Type

from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.chiffrement import AdaptateurChiffrement
from adaptateurs.journal import (
    TypeEvenement,
    DonneesInteractionAjoutee,
    DonneesViolationDetectee,
    AdaptateurJournal,
    DonneesConversationCreee,
    ParagrapheRetourne,
)
from configuration import recupere_configuration
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
from services.exceptions import ErreurRechercheGuidesAnssi, ErreurAppelAlbertApi
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
        if isinstance(e, ErreurRechercheGuidesAnssi):
            self.message_mqc = (
                "Une erreur est survenue lors de la recherche des guides de l'ANSSI."
            )
        elif isinstance(e, ErreurAppelAlbertApi):
            self.message_mqc = "Notre modèle d'IA, Albert, n'a pu nous répondre de manière satisfaisante."
        else:
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
        id_interaction_hachee = configuration.adaptateur_chiffrement.hache(
            str(interaction.id)
        )
        __consigne_l_evenement(
            TypeEvenement.CONVERSATION_CREEE,
            DonneesConversationCreee,
            configuration.adaptateur_journal,
            configuration.adaptateur_chiffrement.hache(
                str(conversation.id_conversation)
            ),
            id_interaction_hachee,
            reponse_question,
            type_utilisateur,
        )

        if reponse_question.violation is not None:
            __consigne_la_violation(
                configuration.adaptateur_journal,
                id_interaction_hachee,
                reponse_question,
            )
        return ResultatConversation(
            conversation.id_conversation,
            reponse_question,
            interaction,
            str(interaction.id),
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
        id_interaction_hachee = configuration.adaptateur_chiffrement.hache(
            str(interaction.id)
        )
        __consigne_l_evenement(
            TypeEvenement.INTERACTION_AJOUTEE,
            DonneesInteractionAjoutee,
            configuration.adaptateur_journal,
            configuration.adaptateur_chiffrement.hache(
                str(conversation.id_conversation)
            ),
            id_interaction_hachee,
            reponse_question,
            type_utilisateur,
        )

        if reponse_question.violation is not None:
            __consigne_la_violation(
                configuration.adaptateur_journal,
                id_interaction_hachee,
                reponse_question,
            )
        return ResultatConversation(
            conversation.id_conversation,
            reponse_question,
            interaction,
            str(interaction.id),
        )
    except Exception as e:
        return ResultatConversationEnErreur(e)


def __consigne_la_violation(
    adaptateur_journal, id_interaction_hachee: str, reponse_question: ReponseQuestion
):
    adaptateur_journal.consigne_evenement(
        type=TypeEvenement.VIOLATION_DETECTEE,
        donnees=DonneesViolationDetectee(
            id_interaction=id_interaction_hachee,
            type_violation=reponse_question.violation.__class__.__name__,
        ),
    )


def __consigne_l_evenement(
    type_evenement: TypeEvenement,
    class_donnees: Type[DonneesConversationCreee | DonneesInteractionAjoutee],
    adaptateur_journal: AdaptateurJournal,
    id_conversation_hachee: str,
    id_interaction_hachee: str,
    reponse_question: ReponseQuestion,
    type_utilisateur: TypeUtilisateur,
) -> None:
    est_alpha_test = recupere_configuration().est_alpha_test
    adaptateur_journal.consigne_evenement(
        type=type_evenement,
        donnees=class_donnees(
            id_conversation=id_conversation_hachee,
            id_interaction=id_interaction_hachee,
            longueur_question=len(reponse_question.question.strip()),
            longueur_reponse=len(reponse_question.reponse.strip()),
            longueur_paragraphes=sum(
                (list(map(lambda r: len(r.contenu), reponse_question.paragraphes)))
            ),
            type_utilisateur=type_utilisateur,
            question=reponse_question.question if est_alpha_test else None,
            sources=list(
                map(
                    lambda r: ParagrapheRetourne(
                        nom_document=r.nom_document, numero_page=r.numero_page
                    ),
                    reponse_question.paragraphes,
                )
            )
            if est_alpha_test
            else None,
        ),
    )


def __cree_interaction(
    question: str,
    reponse_question: ReponseQuestion,
) -> tuple[Interaction, ReponseQuestion]:
    if reponse_question.violation is not None:
        reponse_question = ReponseQuestion(
            reponse=reponse_question.violation.reponse,
            paragraphes=[],
            question=(question),
            question_reformulee=reponse_question.question_reformulee,
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
