import os
import subprocess
import json

from application.path import get_resource_path


class BlenderScriptRunner:
    """
    Klasa obsługująca uruchamianie Blendera w tle z plikami .blend i skryptami Python.
    Pozwala na generowanie obiektów 3D w zależności od typu bramy oraz obsługę dodatków.
    """

    def __init__(self, gate_type="Segmentowa"):
        """
        Inicjalizuje obiekt BlenderScriptRunner, konfigurując ścieżki do plików i ustawienia.

        Args:
            gate_type (str): Typ bramy, np. "Segmentowa", "Uchylna", "Roletowa", "Rozwierana".
        """
        if gate_type == "Brama Segmentowa":
            blend_file = "Segmentowa/segmentowa_kopia3.blend"
            script_file = "Segmentowa/generator_segmentowa.py"
        elif gate_type == "Brama Uchylna":
            blend_file = "Uchylna/uchylna5.blend"
            script_file = "Uchylna/generator_uchylna.py"
        elif gate_type == "Brama Roletowa":
            blend_file = "Roletowa/roletowa7.blend"
            script_file = "Roletowa/generator_roletowa.py"
        elif gate_type == "Brama Rozwierana":
            blend_file = "Rozwierana/rozwierana3.blend"
            script_file = "Rozwierana/generator_rozwierana.py"
        dodatki_script = "dodatki/generowanie_dodatków.py"
        dodatki_blend = "dodatki/uchylna11.blend"

        # Ścieżka do Blendera
        self.blender_path = self._get_default_blender_path()

        # Ścieżki do pliku .blend i skryptu
        self.project_root = os.path.abspath(os.path.dirname(__file__))  # Główny folder projektu
        self.blend_file = os.path.join(self.project_root, blend_file)
        self.script_file = os.path.join(self.project_root, script_file)
        self.blend_file_d = os.path.join(self.project_root, dodatki_blend)
        self.script_file_d = os.path.join(self.project_root, dodatki_script)


    def _get_default_blender_path(self):
        """
        Zwraca domyślną ścieżkę do Blendera na podstawie systemu operacyjnego.

        Returns:
            str: Ścieżka do pliku wykonywalnego Blendera.
        """
        if os.name == 'nt':  # Windows
            return "C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"
        elif os.name == 'posix':  # macOS/Linux
            return "/Applications/Blender.app/Contents/MacOS/Blender"
        else:
            raise EnvironmentError("Nieznany system operacyjny. Podaj ręcznie ścieżkę do Blendera.")

    def validate_paths(self):
        """
        Sprawdza, czy pliki .blend i skrypt istnieją.

        Raises:
            FileNotFoundError: Jeśli którykolwiek z plików nie istnieje.
        """
        if not os.path.exists(self.blend_file):
            raise FileNotFoundError(f"Błąd: Plik .blend nie istnieje: {self.blend_file}")
        if not os.path.exists(self.script_file):
            raise FileNotFoundError(f"Błąd: Skrypt Blenderowy nie istnieje: {self.script_file}")

    def run(self):
        """
        Uruchamia Blendera w tle z plikami .blend i skryptami.
        W przypadku braku wybranych opcji dodatków generuje pusty plik dodatków.
        """
        # Sprawdzanie ścieżek
        self.validate_paths()
        opcje = self.read_json(get_resource_path("resources/selected_options.json"))
        path = get_resource_path("")
        try:
            # Uruchom pierwszy skrypt Blenderowy
            subprocess.run([
                self.blender_path,
                "--background",  # Tryb bez interfejsu graficznego
                self.blend_file,  # Plik .blend do otwarcia
                "--python", self.script_file,  # Skrypt do wykonania
                "--",
                path
            ], check=True)

            if opcje:
                # Uruchom pierwszy skrypt Blenderowy
                subprocess.run([
                    self.blender_path,
                    "--background",  # Tryb bez interfejsu graficznego
                    self.blend_file_d,  # Plik .blend do otwarcia
                    "--python", self.script_file_d,  # Skrypt do wykonania
                    "--",
                    path
                ], check=True)
            else:
                # Jeśli opcje są puste, nadpisujemy plik combined_addons.obj pustym plikiem
                with open(get_resource_path("application/generator/dodatki/combined_addons.obj"), 'w') as f:
                    f.write("# Pusty plik OBJ, ponieważ nie wybrano żadnych dodatków\n")


        except subprocess.CalledProcessError as e:
            print(f"Błąd podczas działania Blendera: {e}")
        except FileNotFoundError:
            print(f"Nie znaleziono Blendera w lokalizacji: {self.blender_path}")

    @staticmethod
    def read_json(json_path):
        """
        Odczytuje wybrane opcje z pliku JSON.

        Args:
            json_path (str): Ścieżka do pliku JSON z opcjami.

        Returns:
            list: Lista elementów dodatków na podstawie wybranych opcji.
        """
        okno = None
        klamka = None
        kratka = None
        drzwi = False  # Domyślna wartość False

        with open(json_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)

            if "Przeszklenia" in existing_data and existing_data["Przeszklenia"] is not None:
                okno = existing_data["Przeszklenia"]
            if "Klamka do bramy" in existing_data and existing_data["Klamka do bramy"] is not None:
                klamka = existing_data["Klamka do bramy"]
            if "Kratka wentylacyjna" in existing_data and existing_data["Kratka wentylacyjna"] is not None:
                kratka = existing_data["Kratka wentylacyjna"]
            if "Opcje dodatkowe" in existing_data and existing_data["Opcje dodatkowe"] is not None:
                dodatki = existing_data["Opcje dodatkowe"]
                if "Drzwi w bramie" in dodatki:
                    drzwi = True

        # Zwracaj tylko elementy, które nie są None lub False
        return [element for element in [okno, klamka, kratka, drzwi] if element]