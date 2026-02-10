import sqlite3

import pytest

from adaptateurs.connecteur import Connecteur
from adaptateurs.migrateur import Migrateur


class ConnecteurSQLite(Connecteur):
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def placeholder(self) -> str:
        return "?"


@pytest.fixture
def temp_migrations_dir(tmp_path):
    d = tmp_path / "migrations"
    d.mkdir()
    return d


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


def test_migrateur_cree_la_table_de_suivi(db_path, temp_migrations_dir):
    conn = ConnecteurSQLite(db_path)
    Migrateur(conn, str(temp_migrations_dir))

    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='migrations_executees'"
    )
    assert cursor.fetchone() is not None
    conn.close()


def test_migrateur_execute_les_migrations_dans_l_ordre(db_path, temp_migrations_dir):
    (temp_migrations_dir / "0001_first.sql").write_text("CREATE TABLE t1 (id INT);")
    (temp_migrations_dir / "0002_second.sql").write_text("CREATE TABLE t2 (id INT);")

    conn = ConnecteurSQLite(db_path)
    migrateur = Migrateur(conn, str(temp_migrations_dir))
    migrateur.execute_migrations()

    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='t1'")
    assert cursor.fetchone() is not None
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='t2'")
    assert cursor.fetchone() is not None

    cursor.execute(
        "SELECT nom_migration FROM migrations_executees ORDER BY nom_migration"
    )
    migrations = cursor.fetchall()
    assert migrations[0][0] == "0001_first.sql"
    assert migrations[1][0] == "0002_second.sql"
    conn.close()


def test_migrateur_est_idempotent(db_path, temp_migrations_dir):
    (temp_migrations_dir / "0001_first.sql").write_text("CREATE TABLE t1 (id INT);")
    conn = ConnecteurSQLite(db_path)
    migrateur = Migrateur(conn, str(temp_migrations_dir))

    migrateur.execute_migrations()
    migrateur.execute_migrations()

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM migrations_executees")
    assert cursor.fetchone()[0] == 1
    conn.close()
