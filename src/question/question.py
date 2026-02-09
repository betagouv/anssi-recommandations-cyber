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
)
from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import (
    Interaction,
    RetourUtilisatrice,
    DonneesCreationRetourUtilisateur,
)
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
        if reponse_question.violation is not None:
            reponse_question = ReponseQuestion(
                reponse=reponse_question.violation.reponse,
                paragraphes=[],
                question=question,
                violation=reponse_question.violation,
            )
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


def ajoute_retour_utilisatrice(
    donnees_ajout_retour: DonneesCreationRetourUtilisateur,
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees,
) -> RetourUtilisatrice | None:
    interaction = adaptateur_base_de_donnees.recupere_interaction(
        uuid.UUID(donnees_ajout_retour.id_interaction)
    )

    if not interaction:
        return None

    interaction.retour_utilisatrice = donnees_ajout_retour.retour
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice(interaction)
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
    adaptateur_base_de_donnees.supprime_retour_utilisatrice(interaction)
    return None
