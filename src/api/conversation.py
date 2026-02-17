from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.chiffrement import (
    AdaptateurChiffrement,
    fabrique_adaptateur_chiffrement,
)
from adaptateurs.journal import AdaptateurJournal, fabrique_adaptateur_journal
from infra.fast_api.fabrique_adaptateur_base_de_donnees import (
    fabrique_adaptateur_base_de_donnees,
)
from question.question import (
    ConfigurationQuestion,
    cree_conversation,
    DemandeConversationUtilisateur,
    ResultatConversation,
    ResultatConversationEnErreur,
    ajoute_interaction,
    DemandeInteractionUtilisateur,
    ResultatConversationInconnue,
)
from schemas.api import (
    QuestionRequete,
    ReponseDemandeConversationAPI,
    ReponseConversationAjouteInteractionAPI,
)
from schemas.type_utilisateur import TypeUtilisateur
from services.fabrique_service_albert import fabrique_service_albert
from services.service_albert import ServiceAlbert

api_conversation = APIRouter(prefix="/conversation")


@api_conversation.post("/")
def route_initie_conversation(
    request: QuestionRequete,
    service_albert: ServiceAlbert = Depends(fabrique_service_albert),
    adaptateur_chiffrement: AdaptateurChiffrement = Depends(
        fabrique_adaptateur_chiffrement
    ),
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees
    ),
    adaptateur_journal: AdaptateurJournal = Depends(fabrique_adaptateur_journal),
    type_utilisateur: str | None = None,
) -> ReponseDemandeConversationAPI:
    question = request.question

    configuration: ConfigurationQuestion = ConfigurationQuestion(
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
        adaptateur_chiffrement=adaptateur_chiffrement,
    )
    resultat_interaction = cree_conversation(
        configuration,
        DemandeConversationUtilisateur(
            question=question,
        ),
        extrais_type_utilisateur(adaptateur_chiffrement, type_utilisateur),
    )

    match resultat_interaction:
        case ResultatConversation():
            return ReponseDemandeConversationAPI(
                **resultat_interaction.reponse_question.model_dump(),
                id_interaction=resultat_interaction.id_interaction,
                id_conversation=str(resultat_interaction.id_conversation),
            )
        case ResultatConversationEnErreur():
            raise HTTPException(
                status_code=422,
                detail={
                    "message": resultat_interaction.message_mqc,
                },
            )


@api_conversation.post("/{id_conversation}", status_code=201)
def route_conversation_ajoute_interaction(
    id_conversation: str,
    request: QuestionRequete,
    service_albert: ServiceAlbert = Depends(fabrique_service_albert),
    adaptateur_chiffrement: AdaptateurChiffrement = Depends(
        fabrique_adaptateur_chiffrement
    ),
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees
    ),
    adaptateur_journal: AdaptateurJournal = Depends(fabrique_adaptateur_journal),
    type_utilisateur: str | None = None,
) -> ReponseConversationAjouteInteractionAPI:
    question = request.question

    configuration: ConfigurationQuestion = ConfigurationQuestion(
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
        adaptateur_chiffrement=adaptateur_chiffrement,
    )
    resultat_interaction = ajoute_interaction(
        configuration,
        DemandeInteractionUtilisateur(
            question=question,
            conversation=UUID(id_conversation),
        ),
        extrais_type_utilisateur(adaptateur_chiffrement, type_utilisateur),
    )
    match resultat_interaction:
        case ResultatConversation():
            return ReponseConversationAjouteInteractionAPI(
                **resultat_interaction.reponse_question.model_dump(),
                id_interaction=str(resultat_interaction.id_interaction),
            )
        case ResultatConversationEnErreur():
            raise HTTPException(
                status_code=422,
                detail={
                    "message": resultat_interaction.message_mqc,
                },
            )
        case ResultatConversationInconnue():
            raise HTTPException(
                status_code=404,
                detail={"message": "La conversation demandée n'existe pas"},
            )


def extrais_type_utilisateur(
    adaptateur_chiffrement: AdaptateurChiffrement, type_utilisateur: str | None
) -> TypeUtilisateur:
    try:
        if (
            type_utilisateur is not None
            and type_utilisateur.startswith("jOr")
            and type_utilisateur[-6] == " "
        ):
            type_utilisateur = type_utilisateur.replace(" ", "+")
        type_utilisateur = (
            TypeUtilisateur(adaptateur_chiffrement.dechiffre(type_utilisateur))
            if type_utilisateur
            else TypeUtilisateur.INCONNU
        )
        if type_utilisateur not in TypeUtilisateur:
            type_utilisateur = TypeUtilisateur.INCONNU
        return type_utilisateur
    except Exception:
        return TypeUtilisateur.INCONNU
