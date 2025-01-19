from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from application.tools.button import StyledButton
import json
import os
from application.tools.path import get_resource_path


class OknoWymiarow(QMainWindow):
    """
    Klasa reprezentująca okno aplikacji do podawania wymiarów bramy garażowej.
    """

    def __init__(self):
        """
        Inicjalizuje okno wymiarów aplikacji.

        Tworzy interfejs użytkownika, ładuje wymiary z pliku JSON (jeśli istnieje)
        oraz przygotowuje pola do wprowadzania danych.
        """
        super().__init__()
        self.setObjectName("OknoWymiarow")  # Dodanie identyfikatora dla stylów
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)
        self.dimensions = {}  # Zmienna do przechowywania wymiarów

        # Initialize UI
        self._setup_ui()

        # Load dimensions from file if available
        self.load_dimensions_from_file()


    def _setup_ui(self):
        """
        Konfiguruje główny układ okna, dzieląc je na panele lewy i prawy.
        """
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Left and Right panels
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()
        right_panel.setObjectName("right_panel")  # Dodanie identyfikatora dla stylów instrukcji

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        main_layout.setStretch(0, 3)  # Left panel is wider
        main_layout.setStretch(1, 2)  # Right panel

    def _create_left_panel(self):
        """
        Tworzy lewy panel z polami wprowadzania wymiarów oraz przyciskami nawigacyjnymi.

        Returns:
            QWidget: Panel z polami tekstowymi i przyciskami.
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self._add_spacer(left_layout)

        # Title label
        dimensions_label = QLabel("Podaj wymiary")
        dimensions_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(dimensions_label)

        # Input field for width
        self.width_layout = QVBoxLayout()
        width_label = QLabel("Szerokość")
        self.width_error_label = QLabel("Minimalna szerokość: 2200 mm")
        self.width_error_label.setStyleSheet("color: red;")
        self.width_error_label.setAlignment(Qt.AlignLeft)
        self.width_error_label.hide()  # Ukryte na początku
        self.width_input = self._create_int_input_field()

        self.width_layout.addWidget(width_label)  # Napis "Szerokość"
        self.width_layout.addWidget(self.width_error_label)  # Komunikat o błędzie
        self.width_layout.addWidget(self.width_input)  # Pole do wprowadzania danych
        left_layout.addLayout(self.width_layout)

        # Input field for height
        self.height_layout = QVBoxLayout()
        height_label = QLabel("Wysokość")
        self.height_error_label = QLabel("Minimalna wysokość: 2000 mm")
        self.height_error_label.setStyleSheet("color: red;")
        self.height_error_label.setAlignment(Qt.AlignLeft)
        self.height_error_label.hide()  # Ukryte na początku
        self.height_input = self._create_int_input_field()

        self.height_layout.addWidget(height_label)  # Napis "Wysokość"
        self.height_layout.addWidget(self.height_error_label)  # Komunikat o błędzie
        self.height_layout.addWidget(self.height_input)  # Pole do wprowadzania danych
        left_layout.addLayout(self.height_layout)

        # Connect textChanged signals to validation
        self.width_input.textChanged.connect(self.validate_inputs)
        self.height_input.textChanged.connect(self.validate_inputs)

        self._add_spacer(left_layout)

        self._add_navigation_buttons(left_layout)

        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return left_widget

    def _create_int_input_field(self):
        """
        Tworzy pole wprowadzania liczb całkowitych z ograniczeniem wartości.

        Returns:
            QLineEdit: Pole wprowadzania danych z walidatorem liczbowym.
        """
        input_field = QLineEdit()
        validator = QIntValidator(1000, 9999)  # Ograniczenie do czterech cyfr
        input_field.setValidator(validator)
        return input_field

    def validate_inputs(self):
        """Enable or disable the accept button based on whether the inputs are filled and valid."""
        width = self.width_input.text()
        height = self.height_input.text()

        # Sprawdzamy, czy liczby są czterocyfrowe i czy są w odpowiednim zakresie
        width_valid = len(width) == 4 and width.isdigit() and int(width) >= 2200
        height_valid = len(height) == 4 and height.isdigit() and int(height) >= 2000

        # Obsługa komunikatów błędów
        self.width_error_label.setVisible(len(width) == 4 and not width_valid)
        self.height_error_label.setVisible(len(height) == 4 and not height_valid)

        # Aktywacja przycisku, jeśli oba pola są poprawne
        self.accept_button.setEnabled(width_valid and height_valid)

    @staticmethod
    def _create_right_panel():
        """
        Tworzy prawy panel zawierający instrukcje dotyczące pomiaru wymiarów.

        Returns:
            QWidget: Panel z opisem kroków pomiaru.
        """
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Instruction label
        instruction_label = QLabel(
            "Instrukcja pomiaru:\n"
            "1. Zmierz wysokość i szerokość otworu.\n"
            "2. Zanotuj dokładne wartości.\n"
            "3. Upewnij się, że pomiary są prawidłowe."
        )
        instruction_label.setWordWrap(True)
        right_layout.addWidget(instruction_label)

        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return right_widget

    @staticmethod
    def _create_int_input(label_text, layout, min_value, max_value):
        """Creates an input field with an integer validator and adds it to the specified layout with a label."""
        label = QLabel(label_text)
        input_field = QLineEdit()

        # Walidator ograniczający wartości do podanego zakresu
        validator = QIntValidator(min_value, max_value)
        input_field.setValidator(validator)

        layout.addWidget(label)
        layout.addWidget(input_field)
        return input_field

    def _add_navigation_buttons(self, layout):
        """
        Dodaje przyciski nawigacyjne („Cofnij” i „Akceptuj”) do podanego układu.

        Args:
            layout (QVBoxLayout): Układ, do którego zostaną dodane przyciski.
        """
        buttons_layout = QHBoxLayout()
        self.back_button = StyledButton("Cofnij")
        self.accept_button = StyledButton("Akceptuj")

        # Początkowo przycisk „Akceptuj” jest wyłączony
        self.accept_button.setEnabled(False)

        # Obsługa kliknięcia przycisku „Akceptuj”
        self.accept_button.clicked.connect(self.save_dimensions)
        self.back_button.clicked.connect(self.clear_json)

        # Add buttons with centered alignment
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.accept_button)
        layout.addLayout(buttons_layout)

    @staticmethod
    def _add_spacer(layout):
        """
        Dodaje odstęp w układzie, aby wyśrodkować elementy w pionie.

        Args:
            layout (QVBoxLayout): Układ, do którego zostanie dodany odstęp.
        """
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def save_dimensions(self):
        """
        Zapisuje wymiary bramy do zmiennej `dimensions` oraz do pliku JSON.
        """
        width = self.width_input.text()
        height = self.height_input.text()

        if width.isdigit() and height.isdigit():
            self.dimensions['Szerokość'] = int(width)
            self.dimensions['Wysokość'] = int(height)

            # Zapisz wymiary do pliku JSON
            self.save_dimensions_to_file()

    def save_dimensions_to_file(self):
        """
        Zapisuje wymiary bramy do pliku JSON w ścieżce ../resources/selected_options.json.
        """
        file_path = get_resource_path("resources/selected_options.json")
        try:
            # Ensure the file exists; if not, create an empty JSON structure
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump({}, file, ensure_ascii=False, indent=4)

            # Load existing data from the file
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Update the dimensions in the file
            data['Wymiary'] = {
                'Szerokość': self.dimensions.get('Szerokość', 0),
                'Wysokość': self.dimensions.get('Wysokość', 0)
            }

            # Save the updated data back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Wystąpił błąd podczas zapisywania wymiarów do pliku: {e}")

    def load_dimensions_from_file(self):
        """
        Wczytuje wymiary z pliku JSON (jeśli istnieje) i aktualizuje pola tekstowe.
        """
        file_path = get_resource_path("resources/selected_options.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                dimensions = data.get('Wymiary', {})
                self.dimensions = dimensions

                # Update input fields with loaded dimensions
                if 'Szerokość' in dimensions:
                    self.width_input.setText(str(dimensions['Szerokość']))
                if 'Wysokość' in dimensions:
                    self.height_input.setText(str(dimensions['Wysokość']))

            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Błąd podczas wczytywania wymiarów: {e}")
        else:
            print(f"Plik {file_path} nie istnieje. Wymiary nie zostały wczytane.")

    @staticmethod
    def clear_json(file_path):
        """
        Czyści plik JSON, zapisując pustą strukturę.

        Args:
            file_path (str): Ścieżka do pliku JSON.
        """
        file_path = get_resource_path("resources/selected_options.json")
        try:
            # Nadpisanie pustą strukturą
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump({}, file, ensure_ascii=False, indent=4)  # Pusty obiekt {}
            print(f"Plik {file_path} został wyczyszczony i zastąpiony pustą strukturą.")
        except Exception as e:
            print(f"Błąd podczas nadpisywania pliku {file_path}: {e}")

