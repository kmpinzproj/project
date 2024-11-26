import os
import subprocess

class BlenderScriptRunner:
    """
    Klasa obsługująca uruchamianie Blendera w tle z plikiem .blend i skryptem Python.
    """
    def __init__(self, gate_type = "Segmentowa"):
        """
        Inicjalizacja obiektu BlenderScriptRunner.
        """
        if gate_type == "Brama Segmentowa":
            blend_file = "Segmentowa/segmentowa_kopia3.blend"
            script_file = "Segmentowa/generator_segmentowa.py"
        elif gate_type == "Brama Uchylna":
            blend_file = "Uchylna/uchylna5.blend"
            script_file = "Uchylna/generator_uchylna.py"
        elif gate_type == "Brama Roletowa":
            blend_file = "Segmentowa/segmentowa_kopia3.blend"
            script_file = "Segmentowa/generator_segmentowa.py"
        elif gate_type == "Brama Rozwierana":
            blend_file = "Segmentowa/segmentowa_kopia3.blend"
            script_file = "Segmentowa/generator_segmentowa.py"

        # Ścieżka do Blendera
        self.blender_path = self._get_default_blender_path()

        # Ścieżki do pliku .blend i skryptu
        self.project_root = os.path.abspath(os.path.dirname(__file__))  # Główny folder projektu
        self.blend_file = os.path.join(self.project_root, blend_file)
        self.script_file = os.path.join(self.project_root, script_file)

    def _get_default_blender_path(self):
        """
        Zwraca domyślną ścieżkę do Blendera na podstawie systemu operacyjnego.
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
        """
        if not os.path.exists(self.blend_file):
            raise FileNotFoundError(f"Błąd: Plik .blend nie istnieje: {self.blend_file}")
        if not os.path.exists(self.script_file):
            raise FileNotFoundError(f"Błąd: Skrypt Blenderowy nie istnieje: {self.script_file}")
        # print("Wszystkie pliki istnieją.")

    def run(self):
        """
        Uruchamia Blendera w tle z podanymi plikami.
        """
        # Sprawdzanie ścieżek
        self.validate_paths()

        # Uruchamianie Blendera
        try:
            subprocess.run([
                self.blender_path,
                "--background",  # Tryb bez interfejsu graficznego
                self.blend_file,  # Plik .blend do otwarcia
                "--python", self.script_file  # Skrypt do wykonania
            ], check=True)
            # print("Blender zakończył działanie pomyślnie.")
        except subprocess.CalledProcessError as e:
            print(f"Błąd podczas działania Blendera: {e}")
        except FileNotFoundError:
            print(f"Nie znaleziono Blendera w lokalizacji: {self.blender_path}")

