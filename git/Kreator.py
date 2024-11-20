from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QCheckBox
)
from PySide6.QtGui import QPixmap
from Rozwijane_menu import ScrollableMenu
from button import StyledButton
import os
import json


class Kreator(QMainWindow):
    LEFT_PANEL_WIDTH = 400
    IMAGE_WIDGET_MIN_SIZE = 400  # Minimum size for image widget

    def __init__(self, gate_type, image_path="cube_render.png"):
        super().__init__()
        self.gate_type = gate_type
        # Poprawiona ścieżka
        self.image_path = os.path.abspath(image_path) if image_path else None
        self.setWindowTitle(f"Kreator - {self.gate_type}")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)
        self.required_fields = self.load_required_fields("wymagane.txt").get(gate_type, [])
        self.default_options = self.load_selected_options("selected_options.json").get(gate_type, {})

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
        """Creates and configures the QLabel widget for image display."""
        image_label = QLabel()
        image_label.setObjectName("imageLabel")
        image_label.setMinimumSize(self.IMAGE_WIDGET_MIN_SIZE, self.IMAGE_WIDGET_MIN_SIZE)
        image_label.setAlignment(Qt.AlignCenter)  # Wyśrodkowanie obrazu

        # Ładowanie obrazka
        if self.image_path and os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)

            if not pixmap.isNull():
                # Dopasowanie obrazu z zachowaniem proporcji
                scaled_pixmap = pixmap.scaled(
                    self.IMAGE_WIDGET_MIN_SIZE,
                    self.IMAGE_WIDGET_MIN_SIZE,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                image_label.setPixmap(scaled_pixmap)
        else:
            image_label.setText("Nie znaleziono obrazka")
            image_label.setAlignment(Qt.AlignCenter)

        return image_label

    def _create_navigation_buttons(self):
        """Creates a widget with 'Back' and 'Save' buttons."""
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        # Create Back and Save buttons
        self.back_button = StyledButton("Cofnij")
        self.save_button = StyledButton("Zapisz")

        self.save_button.clicked.connect(self.validate_and_proceed)

        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.save_button)

        # Remove margins and spacing for navigation buttons
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        return buttons_widget

    def validate_and_proceed(self):
        """Validates required fields and triggers the transition if valid."""
        if self.validate_fields():
            # Pobierz zaznaczone opcje z ScrollableMenu
            self.selected_options = self.navigation_menu.get_selected_options()

            # Zapisz zaznaczone opcje do pliku
            print(f"Zaznaczone opcje: {self.selected_options}")
            self.save_selected_options("selected_options.json", self.gate_type, self.selected_options)
            print("Opcje zapisane do pliku. Przejście do kolejnego widoku...")


    def validate_fields(self):
        """Validates required fields in the ScrollableMenu and returns True if all are valid."""
        return self.navigation_menu.validate_required_fields(self.required_fields)

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
        """Loads selected options for a specific gate type from a JSON file."""
        if not os.path.exists(file_path):
            return {}

        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                return data
            except json.JSONDecodeError:
                print(f"Błąd podczas wczytywania pliku {file_path}.")
                return {}

        return selected_options

    @staticmethod
    def save_selected_options(file_path, gate_type, selected_options):
        """Saves selected options for the current gate type to a JSON file."""
        data = {gate_type: selected_options}  # Dane do zapisania

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Zapisano dane dla {gate_type}: {selected_options}")

    def set_default_options(self):
        """Sets default options based on loaded data."""
        for category, value in self.default_options.items():
            # Obsługa dla opcji checkbox
            if category in self.navigation_menu.option_items_by_category:
                for item in self.navigation_menu.option_items_by_category[category]:
                    if isinstance(item, QCheckBox) and item.text() == value:
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

    def get_selected_options(self):
        """Returns the currently selected options in JSON-friendly format."""
        return self.selected_options