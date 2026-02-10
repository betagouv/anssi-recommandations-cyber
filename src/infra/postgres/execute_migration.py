from adaptateurs.connecteur import ConnecteurPostgresql
from adaptateurs.migrateur import Migrateur
from configuration import recupere_configuration

configuration = recupere_configuration()
migrateur = Migrateur(ConnecteurPostgresql(configuration.base_de_donnees))
migrateur.execute_migrations()
