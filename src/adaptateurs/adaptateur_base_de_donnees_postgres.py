import json
import uuid
from uuid import UUID

import psycopg2
import psycopg2.extras
from typing import Optional, Any

from configuration import recupere_configuration_postgres
from infra.chiffrement.chiffrement import (
    ServiceDeChiffrement,
)
from infra.postgres.encodeurs_json import EncodeurJson
from schemas.retour_utilisatrice import Interaction, Conversation
from .adaptateur_base_de_donnees import AdaptateurBaseDeDonnees

CHEMINS_INTERACTION_A_CONSERVER_EN_CLAIR = [
    "reponse_question/paragraphes/*/score_similarite",
    "reponse_question/paragraphes/*/numero_page",
    "reponse_question/paragraphes/*/url",
    "reponse_question/violation/reponse",
    "retour_utilisatrice/type",
    "retour_utilisatrice/horodatageretour_utilisatrice/tags/*",
]


class AdaptateurBaseDeDonneesPostgres(AdaptateurBaseDeDonnees):
    def __init__(
        self, nom_base_donnees: str, service_chiffrement: ServiceDeChiffrement
    ) -> None:
        config_postgres = recupere_configuration_postgres(nom_base_donnees)
        self._connexion = psycopg2.connect(
            host=config_postgres.hote,
            database=config_postgres.nom,
            user=config_postgres.utilisateur,
            password=config_postgres.mot_de_passe,
            port=config_postgres.port,
        )
        self._connexion.autocommit = True
        self._service_chiffrement = service_chiffrement

    def sauvegarde_interaction(self, interaction: Interaction) -> None:
        interaction_json = self.__chiffre_interaction(interaction.model_dump())
        identifiant_interaction = str(interaction.id)

        interaction_existante = self.recupere_interaction(interaction.id)
        if interaction_existante is not None:
            self._get_curseur().execute(
                "UPDATE interactions SET contenu = %s WHERE id_interaction = %s",
                (interaction_json, identifiant_interaction),
            )
        else:
            self._get_curseur().execute(
                "INSERT INTO interactions (id_interaction, contenu) VALUES (%s, %s)",
                (identifiant_interaction, interaction_json),
            )

    def recupere_interaction(
        self, identifiant_interaction: UUID
    ) -> Optional[Interaction]:
        curseur = self._get_curseur()
        curseur.execute(
            "SELECT id_interaction, contenu FROM interactions WHERE id_interaction = %s",
            (str(identifiant_interaction),),
        )
        ligne = curseur.fetchone()
        if not ligne:
            return None

        interaction_dechiffree = self._service_chiffrement.dechiffre_dict(
            {**ligne["contenu"], "id": ligne["id_interaction"]},
            CHEMINS_INTERACTION_A_CONSERVER_EN_CLAIR,
        )

        return Interaction.model_validate(interaction_dechiffree)

    def __chiffre_interaction(self, dump_interaction: dict[str, Any]) -> str:
        interaction_chiffree = self._service_chiffrement.chiffre_dict(
            dump_interaction,
            CHEMINS_INTERACTION_A_CONSERVER_EN_CLAIR,
        )

        return json.dumps(interaction_chiffree, cls=EncodeurJson)

    def _get_curseur(self):
        return self._connexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def ferme_connexion(self) -> None:
        if self._connexion:
            self._connexion.close()

    def recupere_conversation(self, id_conversation: uuid.UUID) -> Conversation | None:
        curseur = self._get_curseur()
        curseur.execute(
            "SELECT conversations.id AS id_conversation, interactions.id_interaction AS id_interaction, interactions.contenu AS contenu "
            "FROM conversations, interactions WHERE conversations.id = interactions.id_conversation AND id_conversation = %s "
            "ORDER BY contenu ->> 'date_creation' DESC",
            (str(id_conversation),),
        )
        lignes = curseur.fetchall()
        if len(lignes) == 0:
            return None

        les_interactions = []
        for ligne in lignes:
            interaction_dechiffree = self._service_chiffrement.dechiffre_dict(
                {**ligne["contenu"], "id": ligne["id_interaction"]},
                CHEMINS_INTERACTION_A_CONSERVER_EN_CLAIR,
            )

            les_interactions.append(Interaction.model_validate(interaction_dechiffree))
        return Conversation.hydrate(id_conversation, les_interactions)

    def sauvegarde_conversation(self, conversation: Conversation):
        conversation_recuperee = self.recupere_conversation(
            conversation.id_conversation
        )
        if conversation_recuperee is not None:
            ids_existants = {i.id for i in conversation_recuperee.interactions}
            interactions_a_inserer = [
                i for i in conversation.interactions if i.id not in ids_existants
            ]
            interactions_a_mettre_a_jour = [
                i for i in conversation.interactions if i.id in ids_existants
            ]

            if interactions_a_inserer:
                self._insere_toutes_les_interactions(
                    conversation.id_conversation, interactions_a_inserer
                )

            for interaction in interactions_a_mettre_a_jour:
                interaction_json = self.__chiffre_interaction(interaction.model_dump())
                self._mets_a_jour_une_interaction(interaction, interaction_json)
            return
        self._get_curseur().execute(
            "INSERT INTO conversations (id) VALUES (%s)",
            (str(conversation.id_conversation),),
        )

        self._insere_toutes_les_interactions(
            conversation.id_conversation, conversation.interactions
        )

    def _insere_toutes_les_interactions(self, id_conversation, interactions):
        interactions_a_inserer = [
            (
                str(i.id),
                self.__chiffre_interaction(i.model_dump()),
                str(id_conversation),
            )
            for i in interactions
        ]

        psycopg2.extras.execute_values(
            self._get_curseur(),
            "INSERT INTO interactions (id_interaction, contenu, id_conversation) VALUES %s",
            interactions_a_inserer,
        )

    def _mets_a_jour_une_interaction(
        self, interaction: Interaction, interaction_json: str
    ):
        self._get_curseur().execute(
            "UPDATE interactions SET contenu = %s WHERE id_interaction = %s",
            (interaction_json, str(interaction.id)),
        )
