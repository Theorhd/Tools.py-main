class Menu:
    def afficher_menu_connexion(self) -> str:
        """Affiche le menu de connexion principal."""
        print("""
        ====================================
                 MENU PRINCIPAL
        ====================================
        1. Inscription
        2. Connexion
        3. Quitter
        """)

    def afficher_menu(self, role) -> str:
        if role == "admin":
            print("""
            ====================================
                    MENU ADMIN
            ====================================
            1. Ajouter un utilisateur
            2. Supprimer un utilisateur
            3. Modifier un utilisateur
            4. Afficher tous les utilisateurs
            5. Afficher un utilisateur par son ID
            6. Changer le role d'un utilisateur
            7. Accéder au menu utilisateur
            8. Quitter le menu admin
            """)
        elif role == "user":
            print("""
            ====================================
                        Menu
            ====================================
            1. Traduire du texte
            2. Traduire tous les .txt d'un dossier
            3. Démarrer le Chatbot
            4. Quitter
            """)

