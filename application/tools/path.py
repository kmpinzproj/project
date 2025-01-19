import os
import sys

# Rejestracja czcionki
def get_resource_path(relative_path):
    """
    Zwraca ścieżkę do zasobu, uwzględniając środowisko PyInstaller.
    :param relative_path: Relatywna ścieżka do zasobu względem katalogu projektu.
    :return: Absolutna ścieżka do zasobu.
    """
    # Jeśli działa w trybie PyInstaller
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    # Jeśli działa w trybie deweloperskim
    return  "../" + relative_path

def get_persistent_db_path():
    """
    Zwraca ścieżkę do trwałej lokalizacji bazy danych w katalogu użytkownika.
    Jeśli baza danych jeszcze nie istnieje, kopiuje ją z katalogu zasobów.
    """
    # Określ katalog trwały (Windows: AppData, MacOS: Application Support)
    if sys.platform == "win32":
        app_dir = os.path.join(os.getenv("LOCALAPPDATA"), "KreatorBram")
    elif sys.platform == "darwin":
        app_dir = os.path.join(os.getenv("HOME"), "Library", "Application Support", "KreatorBram")
    else:
        app_dir = os.path.join(os.getenv("HOME"), ".kreatorbram")  # Linux

    # Upewnij się, że katalog istnieje
    os.makedirs(app_dir, exist_ok=True)

    # Ścieżka do pliku bazy danych
    db_path = os.path.join(app_dir, "project_db.db")

    return db_path

