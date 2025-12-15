import uuid
import json
import psycopg2
import psycopg2.extras
from typing import Optional, Any
from infra.chiffrement.chiffrement import FournisseurDeServiceDeChiffrement
from infra.postgres.encodeurs_json import EncodeurDeDate
from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction
from schemas.albert import ReponseQuestion
from configuration import recupere_configuration_postgres, recupere_configuration
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
    def __init__(self, nom_base_donnees: str) -> None:
        config_postgres = recupere_configuration_postgres(nom_base_donnees)
        self._connexion = psycopg2.connect(
            host=config_postgres.hote,
            database=config_postgres.nom,
            user=config_postgres.utilisateur,
            password=config_postgres.mot_de_passe,
            port=config_postgres.port,
        )
        self._connexion.autocommit = True
        self._initialise_tables()

    def _initialise_tables(self) -> None:
        self._get_curseur().execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id_interaction TEXT PRIMARY KEY,
                contenu JSONB NOT NULL
            )
        """)

    def sauvegarde_interaction(self, reponse_question: ReponseQuestion) -> str:
        identifiant_interaction = str(uuid.uuid4())

        interaction = Interaction(
            reponse_question=reponse_question, retour_utilisatrice=None
        )
        interaction_json = self.__chiffre_interaction(interaction.model_dump())

        self._get_curseur().execute(
            "INSERT INTO interactions (id_interaction, contenu) VALUES (%s, %s)",
            (identifiant_interaction, interaction_json),
        )
        return identifiant_interaction

    def ajoute_retour_utilisatrice(
        self, identifiant_interaction: str, retour: RetourUtilisatrice
    ) -> Optional[RetourUtilisatrice]:
        interaction = self.recupere_interaction(identifiant_interaction)

        if not interaction:
            return None

        interaction_mise_a_jour = Interaction(
            reponse_question=interaction.reponse_question, retour_utilisatrice=retour
        )
        interaction_json = self.__chiffre_interaction(
            interaction_mise_a_jour.model_dump()
        )

        self._get_curseur().execute(
            "UPDATE interactions SET contenu = %s WHERE id_interaction = %s",
            (interaction_json, identifiant_interaction),
        )
        return retour

    def supprime_retour_utilisatrice(
        self, identifiant_interaction: str
    ) -> Optional[str]:
        interaction = self.recupere_interaction(identifiant_interaction)

        if not interaction:
            return None

        interaction_mise_a_jour = Interaction(
            reponse_question=interaction.reponse_question, retour_utilisatrice=None
        )
        interaction_json = self.__chiffre_interaction(
            interaction_mise_a_jour.model_dump()
        )

        self._get_curseur().execute(
            "UPDATE interactions SET contenu = %s WHERE id_interaction = %s",
            (interaction_json, identifiant_interaction),
        )
        return identifiant_interaction

    def recupere_interaction(
        self, identifiant_interaction: str
    ) -> Optional[Interaction]:
        curseur = self._get_curseur()
        curseur.execute(
            "SELECT contenu FROM interactions WHERE id_interaction = %s",
            (identifiant_interaction,),
        )
        ligne = curseur.fetchone()
        if not ligne:
            return None

        interaction_dechiffree = (
            FournisseurDeServiceDeChiffrement.service.dechiffre_dict(
                ligne["contenu"],
                CHEMINS_INTERACTION_A_CONSERVER_EN_CLAIR,
            )
        )

        return Interaction.model_validate(interaction_dechiffree)

    @staticmethod
    def __chiffre_interaction(dump_interaction: dict[str, Any]) -> str:
        interaction_chiffree = FournisseurDeServiceDeChiffrement.service.chiffre_dict(
            dump_interaction,
            CHEMINS_INTERACTION_A_CONSERVER_EN_CLAIR,
        )

        return json.dumps(interaction_chiffree, cls=EncodeurDeDate)

    def _get_curseur(self):
        return self._connexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def ferme_connexion(self) -> None:
        if self._connexion:
            self._connexion.close()


def fabrique_adaptateur_base_de_donnees_retour_utilisatrice() -> (
    AdaptateurBaseDeDonnees
):
    return AdaptateurBaseDeDonneesPostgres(recupere_configuration().base_de_donnees.nom)
