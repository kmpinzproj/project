from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QCheckBox, QInputDialog,
    QMessageBox, QSpacerItem
)
from application.tools.Rozwijane_menu import ScrollableMenu
from application.tools.button import StyledButton
import os
import json
from application.DatabaseManager import DatabaseManager
from application.generator.generator_gateV2 import BlenderScriptRunner
from application.tools.Widget3D import OpenGLWidget
from application.tools.Kosztorys import PriceCalculator  # Import klasy z pliku Kosztorys.py
from application.tools.path import get_resource_path


class Kreator(QMainWindow):
    """
    Klasa reprezentująca okno kreatora bram garażowych.

    Zarządza interfejsem użytkownika, umożliwia wybór opcji, renderowanie modelu 3D,
    kalkulację kosztów oraz zapis projektu.
    """
    LEFT_PANEL_WIDTH = 400
    IMAGE_WIDGET_MIN_SIZE = 400  # Minimum size for image widget

    def __init__(self):
        """
        Inicjalizuje okno kreatora.
        """
        super().__init__()
        self.setObjectName("kreator_view")
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)

        # Wczytanie opcji z pliku JSON, w tym gate_type
        data = self.load_selected_options(get_resource_path("resources/selected_options.json"))
        self.gate_type = data.get("Typ bramy", "Default")  # Domyślna wartość, jeśli gate_type nie istnieje
        self.default_options = {key: value for key, value in data.items() if key != "Typ bramy"}
        self.required_fields = self.load_required_fields(get_resource_path("resources/wymagane.txt")).get(self.gate_type, [])
        self.selected_options = {}

        # Initialize UI
        self._setup_ui()

        # Ustaw domyślne opcje
        self.set_default_options()

    def _setup_ui(self):
        """
        Konfiguruje główny układ okna, dzieląc go na panel lewy i prawy.
        """
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
        """
        Tworzy lewy panel z menu nawigacyjnym.

        Returns:
            QWidget: Widżet lewego panelu.
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Add scrollable navigation menu
        self.navigation_menu = ScrollableMenu(self.gate_type)
        self.navigation_menu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Ustawienie na elastyczny rozmiar
        left_layout.addWidget(self.navigation_menu)

        return left_widget

    def _create_right_panel(self):
        """
        Tworzy prawy panel zawierający widżet obrazu oraz przyciski nawigacyjne.

        Returns:
            QWidget: Widżet prawego panelu.
        """
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
        """
        Tworzy widżet OpenGL do wyświetlania modelu 3D.

        Returns:
            OpenGLWidget: Widżet OpenGL do renderowania bramy.
        """
        self.gate_render_start()

        # Ścieżka do pliku .obj
        gate_file = get_resource_path("application/generator/model.obj")
        rail_file = get_resource_path("application/generator/szyny.obj")

        # Tworzenie widżetu OpenGL
        self.opengl_widget = OpenGLWidget(gate_file, rail_file)
        return self.opengl_widget

    def gate_render(self):
        """
        Renderuje bramę na podstawie zaznaczonych opcji i aktualizuje widok.
        """
        self.selected_options = self.navigation_menu.get_selected_options()
        self.save_selected_options(get_resource_path("resources/selected_options.json"), self.selected_options)

        # Uruchomienie Blendera za pomocą BlenderScriptRunner
        try:
            gate_type = self.gate_type
            test = BlenderScriptRunner(gate_type)
            test.run()
        except Exception as e:
            print(f"Wystąpił błąd podczas renderowania: {e}")

    def gate_render_start(self):
        """
        Renderuje początkową wersję bramy przy uruchomieniu kreatora.
        """
        self.selected_options = self.navigation_menu.get_selected_options()
        self.save_selected_options(get_resource_path("resources/selected_options.json"), self.default_options)

        # Uruchomienie Blendera za pomocą BlenderScriptRunner
        try:
            gate_type = self.gate_type
            test = BlenderScriptRunner(gate_type)
            test.run()
        except Exception as e:
            print(f"Wystąpił błąd podczas renderowania: {e}")

    def change_model(self):
        """
        Przeładowuje model bramy i szyn w widoku 3D.
        """
        gate_file = get_resource_path("application/generator/model.obj")
        rail_file = get_resource_path("application/generator/szyny.obj")
        addons_file = get_resource_path("application/generator/dodatki/combined_addons.obj")

        if os.path.exists(gate_file) and os.path.exists(rail_file):
            self.opengl_widget.load_model(gate_file)
            self.opengl_widget.load_rails(rail_file)
            if os.path.exists(addons_file):
                self.opengl_widget.load_addons(addons_file)
        else:
            print(f"Nie znaleziono jednego z plików: {gate_file} lub {rail_file}")

    def render_and_change(self):
        """
        Renderuje bramę i odświeża widok modelu 3D.
        """
        self.gate_render()
        self.change_model()

    def _create_navigation_buttons(self):
        """
        Tworzy panel z przyciskami nawigacyjnymi.

        Returns:
            QWidget: Widżet z przyciskami.
        """
        buttons_widget = QWidget()
        main_layout = QVBoxLayout(buttons_widget)

        # Tworzenie głównych wierszy
        row1_layout = QHBoxLayout()
        row2_layout = QHBoxLayout()
        row3_layout = QHBoxLayout()

        # Tworzenie przycisków
        self.render_button = StyledButton("Renderuj")
        self.calculate_price_button = StyledButton("Kalkuluj cenę")
        self.save_button = StyledButton("Zapisz")
        self.contact_button = StyledButton("Przejdź dalej")
        self.back_button = StyledButton("Cofnij")

        self.save_button.clicked.connect(lambda: self.prompt_project_name(False))
        self.render_button.clicked.connect(self.render_and_change)
        self.calculate_price_button.clicked.connect(self.open_cost_calculator)

        # Dodawanie przycisków do wierszy
        row1_layout.addWidget(self.render_button)
        row1_layout.addWidget(self.calculate_price_button)
        row2_layout.addWidget(self.save_button)
        row2_layout.addWidget(self.contact_button)

        # Dodanie przycisku Cofnij w trzecim wierszu (wycentrowany)
        row3_layout.addStretch()
        row3_layout.addWidget(self.back_button)
        row3_layout.addStretch()

        # Dodanie wierszy do głównego układu
        main_layout.addLayout(row1_layout)
        main_layout.addLayout(row2_layout)
        main_layout.addSpacerItem(QSpacerItem(10, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))  # Minimalna przerwa
        main_layout.addLayout(row3_layout)
        main_layout.addSpacerItem(QSpacerItem(10, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))  # Minimalna przerwa

        # Dostosowanie marginesów
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(5)  # Minimalny odstęp między wierszami

        return buttons_widget

    def validate_and_proceed(self):
        """
        Sprawdza wymagane pola i przechodzi do kolejnego widoku, jeśli wszystkie pola są poprawne.

        Returns:
            bool: True, jeśli walidacja zakończyła się sukcesem, False w przeciwnym przypadku.
        """
        if self.validate_fields():

            return self.prompt_project_name()
        else:
            return False

    def validate_fields(self):
        """
        Sprawdza poprawność wymaganych pól w ScrollableMenu.

        Returns:
            bool: True, jeśli wszystkie wymagane pola są poprawne, False w przeciwnym przypadku.
        """
        return self.navigation_menu.validate_required_fields(self.required_fields)

    def prompt_project_name(self, render=False):
        """
        Pyta użytkownika o nazwę projektu i zapisuje projekt.

        Args:
            render (bool): Flaga wskazująca, czy renderowanie powinno zostać wykonane przed zapisem.

        Returns:
            bool: True, jeśli projekt został zapisany, False w przeciwnym przypadku.
        """
        if render:
            self.render_and_change()

        project_name, ok = QInputDialog.getText(self, "Nazwa projektu", "Podaj nazwę projektu:")

        if ok and project_name.strip():
            project_name = project_name.strip()

            # Sprawdzenie, czy projekt istnieje
            should_save = self.check_project_existence_and_prompt(project_name)

            if should_save:
                # Zapisz projekt tylko, jeśli nazwa została podana
                self.selected_options["Nazwa projektu"] = project_name
                self.selected_options.update(self.navigation_menu.get_selected_options())

                # Zapisz zaznaczone opcje do pliku
                self.save_selected_options(get_resource_path("resources/selected_options.json"), self.selected_options)
                self.save_json_to_db(get_resource_path("resources/selected_options.json"), self.selected_options)

                return True  # Projekt został pomyślnie zapisany
            else:
                print("Użytkownik anulował nadpisanie projektu.")
                return False  # Użytkownik anulował nadpisanie
        else:
            print("Anulowano zapis projektu.")
            return False  # Użytkownik anulował zapis

    def check_project_existence_and_prompt(self, project_name):
        """
        Sprawdza, czy projekt o danej nazwie istnieje, i pyta użytkownika o nadpisanie.

        Args:
            project_name (str): Nazwa projektu do sprawdzenia.

        Returns:
            bool: True, jeśli projekt można zapisać, False w przeciwnym przypadku.
        """
        try:
            db_manager = DatabaseManager()
            project_exists = db_manager.check_project_existence(
                project_name)  # Funkcja musi zostać zaimplementowana w DatabaseManager

            if project_exists:
                # Tworzenie okna dialogowego z pytaniem o nadpisanie
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Question)
                msg_box.setWindowTitle("Nadpisz projekt")
                msg_box.setText(f"Projekt o nazwie '{project_name}' już istnieje. Czy chcesz go nadpisać?")
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg_box.setDefaultButton(QMessageBox.No)
                result = msg_box.exec()

                if result == QMessageBox.Yes:
                    return True  # Użytkownik zatwierdził nadpisanie
                else:
                    return False  # Użytkownik anulował operację
            else:
                return True  # Projekt nie istnieje, można kontynuować zapis
        except Exception as e:
            print(f"Wystąpił błąd podczas sprawdzania istnienia projektu: {e}")
            return False

    def set_default_options(self):
        """
        Ustawia domyślne opcje w kreatorze na podstawie załadowanych danych.
        """
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
                    img_label = option_widget.findChild(QLabel, "image_label")

                    if text_label and img_label and text_label.text() == value:
                        self.navigation_menu._on_option_click(category, img_label)  # Kliknięcie na opcję

    def open_cost_calculator(self):
        """
        Otwiera okno kalkulatora cen.
        """
        self.selected_options = self.navigation_menu.get_selected_options()
        self.save_selected_options(get_resource_path("resources/selected_options.json"), self.selected_options)
        self.cost_calculator_window = PriceCalculator()  # Tworzenie instancji okna
        self.cost_calculator_window.show()  # Wyświetlenie okna

    @staticmethod
    def load_required_fields(file_path):
        """
        Wczytuje wymagane pola dla każdego typu bramy z pliku tekstowego.

        Args:
            file_path (str): Ścieżka do pliku tekstowego.

        Returns:
            dict: Słownik z wymaganymi polami dla każdego typu bramy.
        """
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
        """
        Wczytuje zaznaczone opcje z pliku JSON.

        Args:
            file_path (str): Ścieżka do pliku JSON.

        Returns:
            dict: Dane opcji wczytane z pliku JSON.
        """
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
        Zapisuje zaznaczone opcje do pliku JSON.

        Args:
            file_path (str): Ścieżka do pliku JSON.
            selected_options (dict): Dane opcji do zapisania.
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

        # Zapisz dane z powrotem do pliku
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(base_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisywania danych: {e}")

    @staticmethod
    def save_json_to_db(file_path, selected_options):
        """
        Zapisuje dane z pliku JSON do bazy danych.

        Args:
            file_path (str): Ścieżka do pliku JSON.
            selected_options (dict): Dane opcji do zapisania w bazie danych.
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

        # Dodaj projekt do bazy danych
        try:
            db_manager = DatabaseManager()
            db_manager.add_project_from_json(base_data)
        except Exception as e:
            print(f"Wystąpił błąd podczas dodawania projektu do bazy danych: {e}")



