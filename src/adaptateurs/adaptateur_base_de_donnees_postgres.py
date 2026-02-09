import json
from uuid import UUID

import psycopg2
import psycopg2.extras
from typing import Optional, Any

from configuration import recupere_configuration_postgres
from infra.chiffrement.chiffrement import (
    ServiceDeChiffrement,
)
from infra.postgres.encodeurs_json import EncodeurJson
from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction
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
        self._initialise_tables()

    def _initialise_tables(self) -> None:
        self._get_curseur().execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id_interaction TEXT PRIMARY KEY,
                contenu JSONB NOT NULL
            )
        """)

    def sauvegarde_interaction(self, interaction: Interaction) -> None:
        interaction_json = self.__chiffre_interaction(interaction.model_dump())
        identifiant_interaction = str(interaction.id)

        self._get_curseur().execute(
            "INSERT INTO interactions (id_interaction, contenu) VALUES (%s, %s)",
            (identifiant_interaction, interaction_json),
        )

    def ajoute_retour_utilisatrice(
        self, interaction: Interaction
    ) -> Optional[RetourUtilisatrice]:
        interaction_json = self.__chiffre_interaction(interaction.model_dump())

        self._get_curseur().execute(
            "UPDATE interactions SET contenu = %s WHERE id_interaction = %s",
            (interaction_json, str(interaction.id)),
        )
        return interaction.retour_utilisatrice

    def supprime_retour_utilisatrice(self, interaction: Interaction) -> None:
        interaction_json = self.__chiffre_interaction(interaction.model_dump())

        self._get_curseur().execute(
            "UPDATE interactions SET contenu = %s WHERE id_interaction = %s",
            (interaction_json, str(interaction.id)),
        )
        return None

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
