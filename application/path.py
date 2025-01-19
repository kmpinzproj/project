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

def load_qss_with_resources(qss_path):
    """
    Wczytuje plik QSS i zastępuje relatywne ścieżki absolutnymi ścieżkami do zasobów.
    :param qss_path: Relatywna ścieżka do pliku QSS.
    :return: Zmodyfikowany arkusz stylów jako string.
    """
    absolute_qss_path = get_resource_path(qss_path)

    try:
        with open(absolute_qss_path, 'r', encoding='utf-8') as file:
            qss = file.read()

        # Zastąp ścieżki w stylach, np. url(../resources/image.png)
        qss = qss.replace('url(', f'url({get_resource_path("")}/')
        return qss

    except Exception as e:
        print(f"Error loading QSS file: {e}")
        return ""