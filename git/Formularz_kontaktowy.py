from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QMainWindow, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtCore import Qt, QRegularExpression
from button import StyledButton
from generator.szkic.szkic_prosty import (draw_orthogonal_edges, draw_filtered_edges_isometric)
from generator.szkic.szkic_opencv import detect_and_draw_arrows
import os
import json

from git.PDF_Generator import create_pdf


class ContactForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("ContactForm")  # Ustawiamy nazwę klasy CSS
        self.generate_pdf_button = None
        self.invoice_button = None
        self.submit_button = None
        self.back_button = None
        self.comments_input = None
        self.email_input = None
        self.name_input = None
        self.phone_input = None
        self.nip_input = None  # Dodane pole NIP
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)
        self.selected_options = None

        # Set up the main interface
        self.setup_ui()

    def setup_ui(self):
        """Initializes the main layout and divides it into navigation and view panels."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left and Right panels
        navigation_panel = self.create_navigation_panel()
        buttons_panel = self.create_buttons_panel()  # Panel z przyciskami

        main_layout.addWidget(navigation_panel)
        main_layout.addWidget(buttons_panel)

        main_layout.setStretch(0, 2)  # Navigation panel
        main_layout.setStretch(1, 1)  # Buttons panel


    def create_navigation_panel(self):
        """Creates the left panel with contact form fields."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title and subtitle
        title_label = QLabel("Segmentowe. Wyślij zapytanie.")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        subtitle_label = QLabel("Wypełnij formularz kontaktowy. Nasz konsultant skontaktuje się z Tobą.")

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        # Create input fields with labels
        form_layout = QVBoxLayout()
        self.name_input = self._create_form_field("Imię i nazwisko*", QLineEdit(), form_layout)

        # Walidacja pola E-mail
        self.email_input = self._create_form_field("Twój e-mail*", QLineEdit(), form_layout)
        email_regex = QRegularExpression(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        email_validator = QRegularExpressionValidator(email_regex)
        self.email_input.setValidator(email_validator)

        # Walidacja pola Telefon (cyfry i +, maksymalnie 15 znaków)
        self.phone_input = self._create_form_field("Telefon*", QLineEdit(), form_layout)
        phone_regex = QRegularExpression(r'^\+?\d{0,14}$')  # Dozwolone cyfry i + na początku
        phone_validator = QRegularExpressionValidator(phone_regex)
        self.phone_input.setValidator(phone_validator)
        self.phone_input.setMaxLength(15)  # Maksymalnie 15 znaków

        # Walidacja pola NIP (cyfry i myślniki)
        self.nip_input = self._create_form_field("NIP", QLineEdit(), form_layout)
        nip_regex = QRegularExpression(r'^\d{1,3}(-?\d{1,3}){0,3}$')
        nip_validator = QRegularExpressionValidator(nip_regex)
        self.nip_input.setValidator(nip_validator)
        self.nip_input.setMaxLength(13)  # Maksymalnie 13 znaków (123-45-67-890)

        self.comments_input = self._create_form_field("Dodatkowe uwagi", QTextEdit(), form_layout)

        # Podłączenie walidatorów do pól
        self.name_input.textChanged.connect(self.validate_fields)
        self.email_input.textChanged.connect(self.validate_fields)
        self.phone_input.textChanged.connect(self.validate_fields)

        # Add form layout to the main panel layout
        layout.addLayout(form_layout)

        # Upewnij się, że panel i widżety są interaktywne
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        panel.setFocusPolicy(Qt.ClickFocus)

        return panel

    @staticmethod
    def _create_form_field(label_text, widget, layout):
        """Helper function to add a labeled form field to a layout."""
        field_layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 14))
        field_layout.addWidget(label)
        field_layout.addWidget(widget)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed if isinstance(widget, QLineEdit) else QSizePolicy.Expanding)
        layout.addLayout(field_layout)
        return widget

    def create_buttons_panel(self):
        """Creates the right panel with action buttons spread over half the height."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.generate_pdf_button = StyledButton("Generuj PDF")
        self.invoice_button = StyledButton("Generuj Fakturę")
        self.invoice_button.setEnabled(False)  # Domyślnie przycisk jest nieaktywny
        self.submit_button = StyledButton("Start")
        self.back_button = StyledButton("Cofnij")

        self.generate_pdf_button.clicked.connect(self.sketch)
        self.invoice_button.clicked.connect(self.save_to_json)  # Podpięcie przycisku do zapisu JSON

        layout.addWidget(self.generate_pdf_button)
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.invoice_button)
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.submit_button)
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.back_button)

        layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return panel

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

    def save_to_json(self):
        """Zapisuje dane z formularza do pliku JSON."""
        data = {
            "name": self.name_input.text().strip(),
            "email": self.email_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "nip": self.nip_input.text().strip(),
            "comments": self.comments_input.toPlainText().strip()
        }

        output_path = "../resources/invoice_data.json"

        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Dane zapisano do pliku {output_path}")
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisu do pliku {output_path}: {e}")

    def validate_fields(self):
        """Walidacja pól formularza - aktywuje przycisk Kalkulator cen tylko, gdy pola są wypełnione."""
        name_filled = bool(self.name_input.text().strip())
        email_filled = self.email_input.hasAcceptableInput()  # Walidacja formatu e-mail
        phone_filled = bool(self.phone_input.text().strip())

        self.invoice_button.setEnabled(name_filled and email_filled and phone_filled)

    def sketch(self):
        selected_options = self.load_selected_options("../resources/selected_options.json")
        input_obj_file = "../generator/model.obj"
        output_isometric_file = "../generator/sketch_iso_no_diagonals.png"
        output_orthogonal_file = "../generator/sketch_orthogonal.png"
        final_output_path = '../generator/image_with_arrows.png'
        dimensions = selected_options["Wymiary"]
        width = dimensions["Szerokość"]
        height = dimensions["Wysokość"]
        # Generowanie rzutu izometrycznego
        draw_filtered_edges_isometric(input_obj_file, output_isometric_file)
        # Generowanie zwykłego rzutu
        draw_orthogonal_edges(input_obj_file, output_orthogonal_file)

        detect_and_draw_arrows(output_orthogonal_file, final_output_path, width, height)

        create_pdf()

    def sketch(self):
        selected_options = self.load_selected_options("../resources/selected_options.json")
        input_obj_file = "../generator/model.obj"
        output_isometric_file = "../generator/sketch_iso_no_diagonals.png"
        output_orthogonal_file = "../generator/sketch_orthogonal.png"
        final_output_path = '../generator/image_with_arrows.png'
        dimensions = selected_options["Wymiary"]
        width = dimensions["Szerokość"]
        height = dimensions["Wysokość"]
        # Generowanie rzutu izometrycznego
        draw_filtered_edges_isometric(input_obj_file, output_isometric_file)
        # Generowanie zwykłego rzutu
        draw_orthogonal_edges(input_obj_file, output_orthogonal_file)

        detect_and_draw_arrows(output_orthogonal_file, final_output_path, width, height)

        create_pdf()
