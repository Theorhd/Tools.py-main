from contextlib import contextmanager
import sqlite3 as sqlite
import logging
import os

dossier_actuel = os.path.dirname(__file__)
dossier_parent = os.path.dirname(dossier_actuel)
chemin_log = os.path.join(dossier_parent, 'logs', 'db.log')

logging.basicConfig(
    filename=(chemin_log),
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    datefmt="%d/%m/%Y - %H:%M:%S",
    encoding='utf-8'
)

class DB:
    def __init__(self, db_path) -> None:
        self.db_path = db_path

    @contextmanager
    def db_connect(self):
        """Gère la connexion à la base de données SQLite."""
        try:
            conn = sqlite.connect(self.db_path)
            cursor = conn.cursor()
            yield cursor
        except sqlite.Error as e:
            logging.error(f"Erreur lors de la connexion à la base de données : {e}")
        finally:
            conn.commit()
            conn.close()