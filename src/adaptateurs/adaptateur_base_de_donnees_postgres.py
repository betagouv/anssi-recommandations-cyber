import uuid
import psycopg2
import psycopg2.extras
from typing import Dict, Optional
from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction
from schemas.reponses import ReponseQuestion
from config import recupere_configuration_postgres, recupere_configuration
from .adaptateur_base_de_donnees import AdaptateurBaseDeDonnees


class AdaptateurBaseDeDonneesPostgres(AdaptateurBaseDeDonnees):
    def __init__(self, nom_base_donnees: str) -> None:
        config_postgres = recupere_configuration_postgres(nom_base_donnees)
        self._connexion = psycopg2.connect(**config_postgres)
        self._connexion.autocommit = True
        self._initialise_tables()

    def _initialise_tables(self) -> None:
        with self._connexion.cursor() as curseur:
            curseur.execute("""
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

        with self._connexion.cursor() as curseur:
            curseur.execute(
                "INSERT INTO interactions (id_interaction, contenu) VALUES (%s, %s)",
                (identifiant_interaction, interaction.model_dump_json()),
            )
        return identifiant_interaction

    def ajoute_retour_utilisatrice(
        self, identifiant_interaction: str, retour: RetourUtilisatrice
    ) -> bool:
        with self._connexion.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as curseur:
            curseur.execute(
                "SELECT contenu FROM interactions WHERE id_interaction = %s",
                (identifiant_interaction,),
            )
            ligne = curseur.fetchone()
            if not ligne:
                return False

        interaction = Interaction.model_validate(ligne["contenu"])

        interaction_mise_a_jour = Interaction(
            reponse_question=interaction.reponse_question, retour_utilisatrice=retour
        )

        with self._connexion.cursor() as curseur:
            curseur.execute(
                "UPDATE interactions SET contenu = %s WHERE id_interaction = %s",
                (interaction_mise_a_jour.model_dump_json(), identifiant_interaction),
            )
        return True

    def lit_interaction(self, identifiant_interaction: str) -> Optional[Interaction]:
        with self._connexion.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        ) as curseur:
            curseur.execute(
                "SELECT contenu FROM interactions WHERE id_interaction = %s",
                (identifiant_interaction,),
            )
            ligne = curseur.fetchone()
            if not ligne:
                return None

        return Interaction.model_validate(ligne["contenu"])

    def obtient_statistiques(self) -> Dict[str, int]:
        with self._connexion.cursor() as curseur:
            curseur.execute("SELECT COUNT(*) FROM interactions")
            total_interactions = curseur.fetchone()[0]

            curseur.execute("SELECT contenu FROM interactions")
            lignes = curseur.fetchall()
        total_retours = 0
        pouces_leves = 0

        for ligne in lignes:
            interaction = Interaction.model_validate(ligne[0])
            if interaction.retour_utilisatrice is not None:
                total_retours += 1
                if interaction.retour_utilisatrice.pouce_leve:
                    pouces_leves += 1

        return {
            "total_interactions": total_interactions,
            "total_retours": total_retours,
            "pouces_leves": pouces_leves,
        }

    def ferme_connexion(self) -> None:
        if self._connexion:
            self._connexion.close()


def fabrique_adaptateur_base_de_donnees_retour_utilisatrice() -> (
    AdaptateurBaseDeDonnees
):
    return AdaptateurBaseDeDonneesPostgres(recupere_configuration().NOM_BDD)
