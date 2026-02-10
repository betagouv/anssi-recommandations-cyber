import os
import logging

from adaptateurs.connecteur import Connecteur

logger = logging.getLogger(__name__)


class Migrateur:
    def __init__(
        self,
        connecteur: Connecteur,
        repertoire_migrations: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "migrations")
        ),
    ):
        if not os.path.exists(repertoire_migrations):
            logger.info(
                f"Le répertoire de migrations {repertoire_migrations} n'existe pas."
            )
            return
        self._connecteur = connecteur
        self._repertoire_migrations = repertoire_migrations
        self._initialise_table_migrations()

    def _initialise_table_migrations(self):
        curseur = self._connecteur.cursor()
        try:
            curseur.execute("""
                CREATE TABLE IF NOT EXISTS migrations_executees (
                    nom_migration TEXT PRIMARY KEY,
                    date_execution TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self._connecteur.commit()
        finally:
            curseur.close()

    def execute_migrations(self):
        fichiers = sorted(
            [f for f in os.listdir(self._repertoire_migrations) if f.endswith(".sql")]
        )
        nombre_migrations = 0
        for fichier in fichiers:
            if self._migration_deja_executee(fichier):
                logger.debug(f"Migration déjà exécutée : {fichier}")
                continue
            nombre_migrations += 1
            logger.info(f"Exécution de la migration : {fichier}")
            self._execute_fichier_sql(fichier)
            self._enregistre_migration(fichier)
            logger.info(f"Migration {fichier} réussie.")
        logger.info(
            "Aucune migration"
            if nombre_migrations == 0
            else f"Nombre de migrations : {nombre_migrations}"
        )

    def _migration_deja_executee(self, nom_migration: str) -> bool:
        curseur = self._connecteur.cursor()
        try:
            curseur.execute(
                f"SELECT 1 FROM migrations_executees WHERE nom_migration = {self._connecteur.placeholder()}",
                (nom_migration,),
            )
            return curseur.fetchone() is not None
        finally:
            curseur.close()

    def _execute_fichier_sql(self, nom_fichier: str):
        chemin_complet = os.path.join(self._repertoire_migrations, nom_fichier)
        with open(chemin_complet, "r") as f:
            sql = f.read()

        curseur = self._connecteur.cursor()
        try:
            curseur.execute(sql)
            self._connecteur.commit()
        finally:
            curseur.close()

    def _enregistre_migration(self, nom_migration: str):
        curseur = self._connecteur.cursor()
        try:
            curseur.execute(
                f"INSERT INTO migrations_executees (nom_migration) VALUES ({self._connecteur.placeholder()})",
                (nom_migration,),
            )
            self._connecteur.commit()
        finally:
            curseur.close()
