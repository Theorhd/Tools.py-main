import requests
import os
import logging
from PIL import Image
from PIL.ExifTags import TAGS
from plyer import notification

def notify_task_done(task_name: str):
    """Envoie une notification pour indiquer que la tâche est terminée."""
    notification.notify(
        title="Tâche terminée",
        message=f"La tâche '{task_name}' a été exécutée avec succès.",
        timeout=5
    )

class Translate: 
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def translate_text(self, text: str, target_lang: str) -> str:
        """Utilise l'API Google Translate via une requête HTTP pour traduire le texte.

        Args:
            text (str): Texte à traduire
            target_lang (str): Langue dans laquelle traduire le texte d'entrée

        Returns:
            str: Texte traduit
        """
        url = "https://translation.googleapis.com/language/translate/v2"
        max_length = 5000

        translations = []
        for i in range(0, len(text), max_length):
            segment = text[i:i + max_length]
            params = {
                'q': segment,
                'target': target_lang,
                'key': self.api_key
            }
            try:
                response = requests.get(url, params=params)
                response.raise_for_status() 
                translation = response.json()['data']['translations'][0]['translatedText']
                translations.append(translation)
            except requests.exceptions.HTTPError as e:
                logging.warning(f"Erreur {response.status_code} lors de la traduction pour le segment: {segment}")
            except Exception as e:
                logging.warning(f"Erreur lors de la traduction: {e}")
            finally:
                notify_task_done(f"Traduction du texte en {target_lang} réalisé avec succés.")

        return " ".join(translations)

    def translate_txt_files_in_directory(self, directory: str, target_lang: str):
        """Identifie les fichiers .txt dans un dossier, les traduit et enregistre les résultats.

        Args:
            directory (str): Chemin du dossier contenant les fichiers .txt
            target_lang (str): Langue cible pour la traduction
        """
        for filename in os.listdir(directory):
            if filename.endswith('.txt') and '_traduit' not in filename:
                file_path = os.path.join(directory, filename)
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    translation = self.translate_text(content, target_lang)
                    translated_filename = os.path.splitext(filename)[0] + f"_traduit_{target_lang}.txt"
                    translated_file_path = os.path.join(directory, translated_filename)
                    with open(translated_file_path, 'w', encoding='utf-8') as translated_file:
                        translated_file.write(translation)
                    print(f"\nContenu original de {filename} traduit et enregistré dans {translated_filename}")
        notify_task_done(f"Traduction de tout les .txt dans {directory} en {target_lang} réalisé avec succés.")

def translate_input_txt_files(api_key: str):
    """Gère la traduction des fichiers .txt dans un répertoire spécifié par l'utilisateur."""
    directory = input("Saisir le chemin du dossier contenant les fichiers .txt : ")
    target_lang = input("Saisir la langue de traduction : ")

    t = Translate(api_key)
    t.translate_txt_files_in_directory(directory, target_lang)

def translate_input(api_key: str) -> str:
    """Gère la traduction d'un texte saisi par l'utilisateur."""
    texte = input("Saisir le texte à traduire : ")
    target_lang = input("Saisir la langue de traduction : ")

    t = Translate(api_key)
    traduction = t.translate_text(texte, target_lang)

    print(f"""
        Voici votre texte traduit en {target_lang}:

        {traduction}
    """)

logging.info(">> Importation du module tools réalisé avec succès")

from data.db import DB

class ImageAnalyzer:
    def __init__(self, folder_path, db_path):
        self.folder_path = folder_path
        self.db_path = db_path
        self.db = DB(db_path)
        self._create_database()

    def _create_database(self):
        """Création de la table dans la base de données si elle n'existe pas déjà."""
        with self.db.db_connect() as cursor:
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    format TEXT,
                    width INTEGER,
                    height INTEGER,
                    file_size INTEGER,
                    mode TEXT,
                    exif TEXT
                )
            ''')
        logging.info("Table 'images' créée avec succès.")

    def _insert_image_info(self, image_info):
        """Insertion des informations d'une image dans la base de données."""
        with self.db.db_connect() as cursor:
            cursor.execute(''' 
                INSERT INTO images (filename, format, width, height, file_size, mode, exif)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                image_info['filename'],
                image_info.get('format'),
                image_info['size (width, height)'][0],
                image_info['size (width, height)'][1],
                image_info['file_size'],
                image_info.get('mode'),
                str(image_info.get('exif'))
            ))

    def get_image_info(self, image_path):
        """Récupération des informations d'une image et insertion dans la base de données."""
        try:
            with Image.open(image_path) as img:
                image_info = {
                    "filename": os.path.basename(image_path),
                    "format": img.format,
                    "size (width, height)": img.size,
                    "mode": img.mode,
                    "file_size": os.path.getsize(image_path),
                }

                exif_data = img._getexif()
                if exif_data is not None:
                    exif = {
                        TAGS.get(tag): value for tag, value in exif_data.items() if tag in TAGS
                    }
                    image_info["exif"] = exif
                else:
                    image_info["exif"] = "No EXIF data"

                self._insert_image_info(image_info)

                return image_info
        except Exception as e:
            return {"filename": os.path.basename(image_path), "error": str(e)}

    def analyze_images_in_folder(self):
        images_info = []
        for filename in os.listdir(self.folder_path):
            image_path = os.path.join(self.folder_path, filename)
            image_info = self.get_image_info(image_path)
            images_info.append(image_info)
        return images_info

def imageAnalyzer_input(folder:str, db_path:str):
    analyzer = ImageAnalyzer(folder, db_path)
    infos = analyzer.analyze_images_in_folder()
    for info in infos:
        if 'error' in info:
            print(f"Fichier: {info.get('filename')} - Erreur: {info['error']}")
        else:
            print(f"""
            ============================================= 
            Fichier: {info.get('filename')}
            Format: {info.get('format')}
            Dimensions: {info.get('size (width, height)')}
            Taille du fichier: {info.get('file_size')} octets
            Mode: {info.get('mode')}
            EXIF: {info.get('exif')}
            ============================================= 
            """)
    notify_task_done(f"Analyse des images dans {folder} réalisé avec succés.")

class ImageCompressor:
    def __init__(self, input_folder: str, output_folder: str, quality: int = 85):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.quality = quality

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            logging.info(f"Dossier de sortie créé : {output_folder}")

    def compress_image(self, image_path: str):
        """Compresse une image et l'enregistre dans le dossier de sortie."""
        try:
            with Image.open(image_path) as img:
                filename = os.path.basename(image_path)
                output_path = os.path.join(self.output_folder, filename)

                img.save(output_path, format=img.format, quality=self.quality)
                logging.info(f"Image compressée : {output_path}")
        except Exception as e:
            logging.error(f"Erreur lors de la compression de l'image {image_path}: {e}")

    def compress_images_in_folder(self):
        """Parcourt le dossier d'entrée et compresse toutes les images qu'il contient."""
        for filename in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, filename)
            if os.path.isfile(file_path):
                try:
                    with Image.open(file_path) as img:
                        self.compress_image(file_path)
                except (IOError, OSError):
                    logging.warning(f"{filename} n'est pas une image ou ne peut pas être ouverte.")

def compress_images_in_directory(input_folder: str, quality: int = 85):
    """Fonction utilitaire pour compresser les images dans un répertoire."""
    output_folder = os.path.join(input_folder, "images_compressées")
    compressor = ImageCompressor(input_folder, output_folder, quality)
    compressor.compress_images_in_folder()
    notify_task_done(f"Images de {input_folder} compréssées dans {output_folder}")
