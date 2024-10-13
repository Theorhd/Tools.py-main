import os
import logging
from login.login import UserManager
from login.menu import Menu
from tools.tools import translate_input, translate_input_txt_files, ImageAnalyzer, ImageCompressor, imageAnalyzer_input, compress_images_in_directory

# Chemin de la base de données et des logs
dossier_actuel = os.path.dirname(__file__)
DB_PATH = os.path.join(dossier_actuel, 'data', 'app.sqlite3')
chemin_log = os.path.join(dossier_actuel, 'logs', 'app.log')
if not os.path.exists(os.path.join(dossier_actuel, 'logs')):
    os.makedirs(os.path.join(dossier_actuel, 'logs'))
    
# Récupérer la clé API Google Translate depuis le fichier api_key.txt
api_key_path = os.path.join(dossier_actuel, 'api_key.txt')
with open(api_key_path, 'r') as file:
    API_KEY = file.read().strip()

logging.basicConfig(
    filename=(chemin_log),
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    datefmt="%d/%m/%Y - %H:%M:%S",
    encoding='utf-8'
)

class Application:
    def __init__(self):
        self.user_manager = UserManager(DB_PATH)
        self.menu = Menu()

    def run(self):
        """Méthode principale qui démarre l'application et affiche les menus selon les rôles."""
        self.user_manager.init_db()

        while True:
            self.menu.afficher_menu_connexion()
            choix = input("Choisissez une option : ")

            if choix == "1":
                self.user_manager.register()
            elif choix == "2":
                user = self.user_manager.login()
                if user:
                    self.menu.afficher_menu(user['role'])
                    self.menu_actions(user)
            elif choix == "3":
                print("Merci d'avoir utilisé l'application. Au revoir!")
                logging.info("Fermeture de l'application.")
                break
            else:
                print("Option invalide, veuillez réessayer.")
                logging.warning(f"Option invalide sélectionnée : {choix}")

    def menu_actions(self, user):
        """Méthode pour gérer les actions selon le rôle de l'utilisateur (admin ou user)."""
        while True:
            if user['role'] == 'admin':
                self.menu.afficher_menu(user['role'])
                choix = input("Choisissez une option : ")

                if choix == "1":
                    self.user_manager.add_user()
                elif choix == "2":
                    self.user_manager.delete_user()
                elif choix == "3":
                    self.user_manager.modify_user()
                elif choix == "4":
                    self.user_manager.display_all_users()
                elif choix == "5":
                    self.user_manager.get_user_by_id()
                elif choix == "6":
                    self.user_manager.change_role()
                elif choix == "8":
                    break
                else:
                    print("Option invalide, veuillez réessayer.")
            elif user['role'] == 'user':
                self.menu_user_actions()
                break

    def menu_user_actions(self):
        """Méthode pour gérer les actions disponibles pour l'utilisateur."""
        while True:

            choix = input("Votre choix : ")
            if choix == "1":
                translate_input(API_KEY)
            elif choix == "2":
                translate_input_txt_files(API_KEY)
            elif choix == "3":
                dossier_images = input("Chemin du dossier contenant les images : ")
                db_path = os.path.join('data', 'imageAnalyzer.sqlite3')
                imageAnalyzer_input(dossier_images, db_path)
            elif choix == "4":
                input_folder = input("Saisir le chemin du dossier contenant les images à compresser : ")
                quality = int(input("Saisir le niveau de qualité (1 à 100) : "))
                compress_images_in_directory(input_folder, quality)
                print("Compression des images terminée.")
            elif choix == "5":
                break
            else:
                print("Option invalide, veuillez réessayer.")

if __name__ == "__main__":
    app = Application()
    app.run()
