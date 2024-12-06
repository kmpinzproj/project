from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QCheckBox, QGridLayout, QInputDialog
)
from PySide6.QtGui import QPixmap
from Rozwijane_menu import ScrollableMenu
from button import StyledButton
import os
import json
from git.DatabaseManager import DatabaseManager
from generator.generator_gateV2 import BlenderScriptRunner
from Widget3D import OpenGLWidget

if __name__ == "__main__":
    runner = BlenderScriptRunner()
    runner.run()


class Kreator(QMainWindow):
    LEFT_PANEL_WIDTH = 400
    IMAGE_WIDGET_MIN_SIZE = 400  # Minimum size for image widget

    def __init__(self, test, image_path="../generator/renders/Camera_4.png"):
        super().__init__()
        self.setObjectName("kreator_view")
        self.image_path = os.path.abspath(image_path) if image_path else None
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)

        # Wczytanie opcji z pliku JSON, w tym gate_type
        data = self.load_selected_options("../resources/selected_options.json")
        self.gate_type = data.get("Typ bramy", "Default")  # Domyślna wartość, jeśli gate_type nie istnieje
        self.default_options = {key: value for key, value in data.items() if key != "Typ bramy"}
        self.required_fields = self.load_required_fields("../resources/wymagane.txt").get(self.gate_type, [])
        self.selected_options = {}
        # Initialize UI
        self._setup_ui()

        # Ustaw domyślne opcje
        self.set_default_options()

    def _setup_ui(self):
        """Sets up the main layout and divides it into left and right panels."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Tworzenie lewego i prawego panelu
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        # Dodaj panele do głównego układu
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        # Ustaw proporcje rozciągania dla lewego i prawego panelu
        main_layout.setStretch(0, 1)  # Lewy panel
        main_layout.setStretch(1, 1)  # Prawy panel, równomierna proporcja do lewego panelu

    def _create_left_panel(self):
        """Creates the left panel with the scrollable menu based on gate type."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Add scrollable navigation menu
        self.navigation_menu = ScrollableMenu(self.gate_type)
        self.navigation_menu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Ustawienie na elastyczny rozmiar
        left_layout.addWidget(self.navigation_menu)

        return left_widget

    def _create_right_panel(self):
        """Creates the right panel with QLabel for image display and navigation buttons."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # QLabel widget for image display
        image_widget = self._create_image_widget()
        right_layout.addWidget(image_widget)

        # Navigation buttons at the bottom
        buttons_widget = self._create_navigation_buttons()
        right_layout.addWidget(buttons_widget)

        return right_widget

    def _create_image_widget(self):
        """Creates and configures the OpenGLWidget for 3D display."""
        self.gate_render_start()

        # Ścieżka do pliku .obj
        gate_file = "../generator/model.obj"
        rail_file = "../generator/szyny.obj"

        # Tworzenie widżetu OpenGL
        self.opengl_widget = OpenGLWidget(gate_file, rail_file)
        return self.opengl_widget

    def gate_render(self):
        """
        Renderuje bramę za pomocą BlenderScriptRunner i aktualizuje obrazek w interfejsie.
        """
        self.selected_options = self.navigation_menu.get_selected_options()
        self.save_selected_options("../resources/selected_options.json", self.selected_options)
        # Uruchomienie Blendera za pomocą BlenderScriptRunner
        try:
            gate_type = self.gate_type
            test = BlenderScriptRunner(gate_type)
            test.run()
        except Exception as e:
            print(f"Wystąpił błąd podczas renderowania: {e}")

    def gate_render_start(self):
        """
        Renderuje bramę za pomocą BlenderScriptRunner i aktualizuje obrazek w interfejsie.
        """
        self.selected_options = self.navigation_menu.get_selected_options()
        self.save_selected_options("../resources/selected_options.json", self.default_options)
        # Uruchomienie Blendera za pomocą BlenderScriptRunner
        try:
            gate_type = self.gate_type
            test = BlenderScriptRunner(gate_type)
            test.run()
        except Exception as e:
            print(f"Wystąpił błąd podczas renderowania: {e}")

    def change_model(self):
        """Zmienia model na nowy i przeładowuje widok 3D."""
        # Ścieżka do pliku .obj
        gate_file = "../generator/model.obj"
        rail_file = "../generator/szyny.obj"

        if os.path.exists(gate_file):
            self.opengl_widget.load_model(gate_file)  # Przeładuj model w widżecie OpenGL
            self.opengl_widget.load_rails(rail_file)
        else:
            print(f"Nie znaleziono pliku modelu: {gate_file}")

    def render_and_change(self):
        self.gate_render()
        self.change_model()

    def _create_navigation_buttons(self):
        """Creates a widget with 'Back', 'Save', 'Render', and 'Contact' buttons."""
        buttons_widget = QWidget()
        buttons_layout = QGridLayout(buttons_widget)  # Zamiast QHBoxLayout używamy QGridLayout

        # Create Back, Save, Render, and Contact buttons
        self.back_button = StyledButton("Cofnij")
        self.contact_button = StyledButton("Kontakt")
        self.render_button = StyledButton("Renderuj")
        self.save_button = StyledButton("Zapisz")

        self.save_button.clicked.connect(lambda: self.prompt_project_name(True))
        self.render_button.clicked.connect(self.render_and_change)

        # Dodaj przyciski w układzie 2x2
        buttons_layout.addWidget(self.render_button, 0, 0)  # Wiersz 0, kolumna 0
        buttons_layout.addWidget(self.save_button, 0, 1)  # Wiersz 0, kolumna 1
        buttons_layout.addWidget(self.back_button, 1, 0)  # Wiersz 1, kolumna 0
        buttons_layout.addWidget(self.contact_button, 1, 1)  # Wiersz 1, kolumna 1

        # Usuń marginesy i odstępy dla przycisków
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)  # Odstęp między przyciskami

        return buttons_widget

    def validate_and_proceed(self):
        """Validates required fields and triggers the transition if valid."""
        if self.validate_fields():
            # print("Przeszło walidacje")
            # Pobierz zaznaczone opcje z ScrollableMenu
            # self.selected_options = self.navigation_menu.get_selected_options()

            # Zapisz zaznaczone opcje do pliku
            # print(f"Zaznaczone opcje: {self.selected_options}")
            self.prompt_project_name()
            # print("Opcje zapisane do pliku. Przejście do kolejnego widoku...")
            return True
        else:
            # print("Dlaczego działasz drugi raz?")
            return False

    def validate_fields(self):
        """Validates required fields in the ScrollableMenu and returns True if all are valid."""
        return self.navigation_menu.validate_required_fields(self.required_fields)

    def prompt_project_name(self, render = False):
        """Prompt user for a project name before saving."""
        if render == True:
            self.render_and_change()
        project_name, ok = QInputDialog.getText(self, "Nazwa projektu", "Podaj nazwę projektu:")
        if ok and project_name.strip():
            # Zapisz projekt tylko, jeśli nazwa została podana
            self.selected_options["Nazwa projektu"] = project_name.strip()
            self.selected_options.update(self.navigation_menu.get_selected_options())

            # Zapisz zaznaczone opcje do pliku
            self.save_selected_options("../resources/selected_options.json", self.selected_options)
            self.save_json_to_db("../resources/selected_options.json", self.selected_options)

            print("Projekt został zapisany.")
            return True  # Projekt został pomyślnie zapisany
        else:
            print("Anulowano zapis projektu.")
            return False  # Użytkownik anulował zapis



    def set_default_options(self):
        """Sets default options based on loaded data."""
        for category, value in self.default_options.items():
            # Obsługa dla opcji checkbox (pojedyncze i wielokrotne)
            if category in self.navigation_menu.option_items_by_category:
                for item in self.navigation_menu.option_items_by_category[category]:
                    if isinstance(item, QCheckBox):
                        if isinstance(value, list):
                            # Jeśli wartość to lista, zaznacz checkboxy odpowiadające każdej wartości
                            if item.text() in value:
                                item.setChecked(True)
                        else:
                            # Jeśli wartość to pojedynczy tekst, zaznacz odpowiedni checkbox
                            if item.text() == value:
                                item.setChecked(True)

            # Obsługa dla opcji z obrazkami (Kolory, Układ wypełnienia itp.)
            if category in self.navigation_menu.option_items_by_category:
                for option_widget in self.navigation_menu.option_items_by_category[category]:
                    text_label = option_widget.findChild(QLabel, "text_label")
                    if text_label and text_label.text() == value:
                        img_label = option_widget.findChild(QLabel, "image_label")
                        if img_label:
                            # Zaznacz opcję poprzez obramowanie
                            img_label.setStyleSheet("border: 2px solid red; padding: 0px; margin: 0px;")
                            # Aktualizuj zaznaczoną opcję w selected_options
                            self.navigation_menu.selected_options[category] = value

        # Specjalna obsługa dla kategorii "Kolor"
        if "Kolor" in self.default_options:
            kolor_value = self.default_options["Kolor"]

            # Szukaj w "Kolor Standardowy" i "Kolor RAL"
            for color_category in ["Kolor Standardowy", "Kolor RAL"]:
                if color_category in self.navigation_menu.option_items_by_category:
                    for option_widget in self.navigation_menu.option_items_by_category[color_category]:
                        text_label = option_widget.findChild(QLabel, "text_label")
                        if text_label and text_label.text() == kolor_value:
                            img_label = option_widget.findChild(QLabel, "image_label")
                            if img_label:
                                # Zaznacz opcję w odpowiedniej kategorii
                                img_label.setStyleSheet("border: 2px solid red; padding: 0px; margin: 0px;")
                                # Zaktualizuj klucz "Kolor" w selected_options
                                self.navigation_menu.selected_options["Kolor"] = kolor_value

    @staticmethod
    def load_required_fields(file_path):
        """Loads required fields for each gate type from a text file."""
        required_fields = {}
        current_gate_type = None

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue  # Pomijamy puste linie

                if line.startswith('[') and line.endswith(']'):
                    # Nowy typ bramy
                    current_gate_type = line[1:-1]
                    required_fields[current_gate_type] = []
                elif current_gate_type:
                    # Dodaj opcję do bieżącego typu bramy
                    required_fields[current_gate_type].append(line)

        return required_fields

    @staticmethod
    def load_selected_options(file_path):
        """Loads selected options from a JSON file."""
        if not os.path.exists(file_path):
            print(f"Plik {file_path} nie istnieje. Zwracanie pustych opcji.")
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data  # Zwraca pełne dane z JSON-a, w tym gate_type
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Błąd podczas wczytywania pliku {file_path}: {e}")
            return {}

    @staticmethod
    def save_selected_options(file_path, selected_options):
        """
        Saves selected options to a JSON file by preserving 'Typ bramy' and 'Wymiary',
        and overwriting all other data with new selected options.
        """
        # Przygotuj bazową strukturę danych
        base_data = {}

        # Wczytaj istniejące dane z pliku JSON, jeśli plik istnieje
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    existing_data = json.load(file)
                    # Zachowaj 'Typ bramy' i 'Wymiary'
                    if "Typ bramy" in existing_data:
                        base_data["Typ bramy"] = existing_data["Typ bramy"]
                    if "Wymiary" in existing_data:
                        base_data["Wymiary"] = existing_data["Wymiary"]
            except (json.JSONDecodeError, FileNotFoundError):
                print(f"Nie udało się wczytać istniejącego pliku {file_path}. Użycie pustej struktury.")

        # Połącz dane bazowe z nowymi wybranymi opcjami
        base_data.update(selected_options)
        # print(selected_options)

        # Zapisz dane z powrotem do pliku
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(base_data, file, ensure_ascii=False, indent=4)
                # print(f"Dane zostały zapisane w pliku {file_path}.")
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisywania danych: {e}")

    @staticmethod
    def save_json_to_db(file_path, selected_options):
        # Przygotuj bazową strukturę danych
        base_data = {}

        # Wczytaj istniejące dane z pliku JSON, jeśli plik istnieje
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    existing_data = json.load(file)
                    # Zachowaj 'Typ bramy' i 'Wymiary'
                    if "Typ bramy" in existing_data:
                        base_data["Typ bramy"] = existing_data["Typ bramy"]
                    if "Wymiary" in existing_data:
                        base_data["Wymiary"] = existing_data["Wymiary"]
            except (json.JSONDecodeError, FileNotFoundError):
                print(f"Nie udało się wczytać istniejącego pliku {file_path}. Użycie pustej struktury.")

        # Połącz dane bazowe z nowymi wybranymi opcjami
        base_data.update(selected_options)

        # Dodaj projekt do bazy danych
        try:
            db_manager = DatabaseManager()
            db_manager.add_project_from_json(base_data)
        except Exception as e:
            print(f"Wystąpił błąd podczas dodawania projektu do bazy danych: {e}")



