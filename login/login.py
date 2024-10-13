import os
import logging
import hashlib
from data.db import DB

dossier_actuel = os.path.dirname(__file__)
dossier_parent = os.path.dirname(dossier_actuel)
chemin_log = os.path.join(dossier_parent, 'logs', 'login.log')
if not os.path.exists(os.path.join(dossier_parent, 'logs')):
    os.makedirs(os.path.join(dossier_parent, 'logs'))

db_path = os.path.join(dossier_parent, 'data', 'app.sqlite3')
if not os.path.exists(os.path.join(dossier_parent, 'data')):
    os.makedirs(os.path.join(dossier_parent, 'data'))

logging.basicConfig(
    filename=(chemin_log),
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    datefmt="%d/%m/%Y - %H:%M:%S",
    encoding='utf-8'
)
logging.info(">> Importation du module login ...")

class UserManager:
    def __init__(self, db_path) -> None:
        self.db_path = db_path
        self.db = DB(db_path)
        self.init_db()

    def init_db(self) -> None:
        """Initialise la base de données en créant la table users si elle n'existe pas."""
        with self.db.db_connect() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(30) NOT NULL UNIQUE,
                    password VARCHAR(64) NOT NULL,
                    role VARCHAR(10) NOT NULL DEFAULT 'user'
                )
            ''')
        logging.info("Base de données initialisée avec succès.")


    def hash_password(self, password: str) -> str:
        """Hash le mot de passe avec sha256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self) -> None:
        """Inscrit un nouvel utilisateur."""
        username = input("Username : ")
        password = self.hash_password(input("Password : "))
        role = 'user'
        with self.db.db_connect() as cursor:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            logging.info(f"Utilisateur '{username}' ajouté avec succès.")
            print(f"Utilisateur '{username}' ajouté avec succès.")

    def login(self) -> None:
        """Authentifie un utilisateur par son nom d'utilisateur et son mot de passe."""
        username = input("Username : ")
        password = self.hash_password(input("Password : "))
        with self.db.db_connect() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                logging.info(f"Utilisateur {username} authentifié avec succès.")
                print(f"Bienvenue, {username}!")
                return {"username": user[1], "role": user[3]}
            else:
                logging.warning(f"Échec d'authentification pour l'utilisateur {username}.")
                print(f"Échec d'authentification pour l'utilisateur '{username}'.")
                return None

    def delete_user(self) -> None:
        """Supprime un utilisateur."""
        username = input("Username à supprimer : ")
        with self.db.db_connect() as cursor:
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            if cursor.rowcount > 0:
                logging.info(f"Utilisateur {username} supprimé avec succès.")
                print(f"Utilisateur '{username}' supprimé avec succès.")
            else:
                logging.warning(f"L'utilisateur {username} n'a pas été trouvé.")
                print(f"Utilisateur '{username}' non trouvé.")

    def modify_user(self) -> None:
        """Modifie le mot de passe d'un utilisateur."""
        username = input("Username à modifier : ")
        new_password = self.hash_password(input("Nouveau mot de passe : "))
        with self.db.db_connect() as cursor:
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
            if cursor.rowcount > 0:
                logging.info(f"Mot de passe de {username} modifié avec succès.")
                print(f"Mot de passe de '{username}' modifié avec succès.")
            else:
                logging.warning(f"L'utilisateur {username} n'a pas été trouvé.")
                print(f"Utilisateur '{username}' non trouvé.")

    def display_all_users(self) -> str:
        """Affiche tous les utilisateurs."""
        with self.db.db_connect() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            logging.info("Récupération de tous les utilisateurs réussie.")
            print(f"Liste des utilisateurs :")
            for user in users:
                print(f"""
                                Utilisateur {user[0]}
                    ====================================================
                            ID_utilisateur: {user[0]}
                            Username: {user[1]}
                            Password: {user[2]}
                            Role: {user[3]}
                    ====================================================
                """)

    def get_user_by_id(self) -> str:
        """Affiche les informations d'un Utilisateur par son ID"""
        user_id = input("ID de l'utilisateur : ")
        with self.db.db_connect() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            logging.info(f"Récupération des informations de l'utilisateur {user_id} réalisée avec succès.")
            print(f"""
                            Utilisateur {user_id}
                ====================================================
                            ID_utilisateur: {user[0]}
                            Username: {user[1]}
                            Password: {user[2]}
                            Role: {user[3]}
                ====================================================
            """)

    def change_role(self) -> None:
        """Change le rôle d'un Utilisateur"""
        username = input("Username : ")
        role = input("Role [user/admin] : ")
        with self.db.db_connect() as cursor:
            cursor.execute("UPDATE users SET role = ? WHERE username = ?", (role, username))
            if cursor.rowcount > 0:
                logging.info(f"Le rôle de l'utilisateur '{username}' a bien été modifié pour '{role}'.")
                print(f"Le rôle de l'utilisateur '{username}' a bien été modifié pour '{role}'.")
            else:
                print(f"Erreur lors du changement du rôle.")
                logging.warning(f"Erreur lors du changement du rôle de '{username}' pour '{role}'.")

logging.info(">> Importation du module login réalisée avec succès.")
