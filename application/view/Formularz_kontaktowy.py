from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QMainWindow, QSizePolicy, QSpacerItem, QApplication, QFileDialog
)
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtCore import Qt, QRegularExpression
from application.tools.button import StyledButton
from application.generator.szkic.szkic_prosty import (draw_orthogonal_edges, draw_filtered_edges_isometric)
from application.generator.szkic.szkic_opencv import detect_and_draw_arrows
from application.generator.PDF.InvoiceGenerator import InvoiceGenerator
import os
import json
from application.path import get_resource_path

from application.generator.PDF.PDF_Generator import PDFGenerator


class ContactForm(QMainWindow):
    """
    Klasa reprezentująca formularz kontaktowy dla aplikacji Garage Door Designer.

    Formularz umożliwia wprowadzenie danych kontaktowych, uwag oraz generowanie faktur
    i plików PDF z podglądem bramy.
    """
    def __init__(self):
        """
        Inicjalizuje widok formularza kontaktowego oraz jego interfejs użytkownika.
        """
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
        """
        Tworzy główny układ interfejsu, dzieląc go na panel nawigacyjny oraz panel przycisków.
        """
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
        """
        Tworzy lewy panel zawierający pola formularza kontaktowego.

        Returns:
            QWidget: Panel z polami formularza kontaktowego.
        """
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
        """
        Tworzy pole formularza z podaną etykietą i widżetem.

        Args:
            label_text (str): Tekst etykiety.
            widget (QWidget): Widżet do wprowadzania danych.
            layout (QVBoxLayout): Układ, do którego zostanie dodane pole formularza.

        Returns:
            QWidget: Utworzony widżet formularza.
        """
        field_layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setFont(QFont("Arial", 14))
        field_layout.addWidget(label)
        field_layout.addWidget(widget)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed if isinstance(widget, QLineEdit) else QSizePolicy.Expanding)
        layout.addLayout(field_layout)
        return widget

    def create_buttons_panel(self):
        """
        Tworzy prawy panel z przyciskami akcji.

        Returns:
            QWidget: Panel z przyciskami.
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)

        layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.generate_pdf_button = StyledButton("Generuj PDF")
        self.invoice_button = StyledButton("Generuj Fakturę")
        self.invoice_button.setEnabled(False)  # Domyślnie przycisk jest nieaktywny
        self.submit_button = StyledButton("Start")
        self.back_button = StyledButton("Cofnij")

        self.generate_pdf_button.clicked.connect(self.sketch)
        self.invoice_button.clicked.connect(self.generate_invoice)  # Podpięcie przycisku do zapisu JSON

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
        """
        Wczytuje zaznaczone opcje z pliku JSON.

        Args:
            file_path (str): Ścieżka do pliku JSON.

        Returns:
            dict: Wczytane dane w formie słownika.
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

    def generate_invoice(self):
        """
        Generuje fakturę na podstawie danych z formularza i zapisuje ją do pliku JSON.
        """
        data = {
            "Imię i nazwisko": self.name_input.text().strip(),
            "Adres e-mail": self.email_input.text().strip(),
            "Nr telefonu": self.phone_input.text().strip(),
            "NIP": self.nip_input.text().strip(),
            "Uwagi:": self.comments_input.toPlainText().strip()
        }

        output_path = get_resource_path("resources/invoice_data.json")

        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Dane zapisano do pliku {output_path}")
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisu do pliku {output_path}: {e}")

        try:
            save_window = QApplication.instance()
            if not save_window:
                save_window = QApplication([])

            # Prompt the user to choose the save location for the PDF
            output_path, _ = QFileDialog.getSaveFileName(
                None,
                "Save PDF File",
                os.path.expanduser("~/"),
                "PDF files (*.pdf)"
            )

            if not output_path:
                print("No file selected for saving the PDF.")
                return

            # Remove the existing file if it exists
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except PermissionError as e:
                    print(f"Error: Unable to delete the existing PDF file. {e}")
                    return

            invoice_generator = InvoiceGenerator(output_path=output_path)
            invoice_generator.generate_invoice()
            print("Faktura PDF została wygenerowana pomyślnie.")
        except Exception as e:
            print(f"Wystąpił błąd podczas generowania faktury PDF: {e}")

    def validate_fields(self):
        """
        Waliduje pola formularza i aktywuje przycisk faktury, jeśli dane są poprawne.
        """
        name_filled = bool(self.name_input.text().strip())
        email_filled = self.email_input.hasAcceptableInput()  # Walidacja formatu e-mail
        phone_filled = bool(self.phone_input.text().strip())

        self.invoice_button.setEnabled(name_filled and email_filled and phone_filled)

    def sketch(self):
        """
         Generuje podgląd i szkice na podstawie wybranych opcji oraz zapisuje je w formacie PDF.
         """
        selected_options = self.load_selected_options(get_resource_path("resources/selected_options.json"))
        input_obj_file = get_resource_path("application/generator/model.obj")
        output_isometric_file = get_resource_path("application/generator/szkic/sketch_iso_no_diagonals.png")
        output_orthogonal_file = get_resource_path("application/generator/szkic/sketch_orthogonal.png")
        final_output_path = get_resource_path("application/generator/szkic/image_with_arrows.png")
        dimensions = selected_options["Wymiary"]
        width = dimensions["Szerokość"]
        height = dimensions["Wysokość"]
        # Generowanie rzutu izometrycznego
        draw_filtered_edges_isometric(input_obj_file, output_isometric_file)
        # Generowanie zwykłego rzutu
        draw_orthogonal_edges(input_obj_file, output_orthogonal_file)

        detect_and_draw_arrows(output_orthogonal_file, final_output_path, width, height)

        try:
            save_window = QApplication.instance()
            if not save_window:
                save_window = QApplication([])

            # Prompt the user to choose the save location for the PDF
            output_path, _ = QFileDialog.getSaveFileName(
                None,
                "Save PDF File",
                os.path.expanduser("~/"),
                "PDF files (*.pdf)"
            )

            if not output_path:
                print("No file selected for saving the PDF.")
                return

            # Remove the existing file if it exists
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except PermissionError as e:
                    print(f"Error: Unable to delete the existing PDF file. {e}")
                    return

            pdf_generator = PDFGenerator(output_path=output_path)
            pdf_generator.create_pdf()
            print("Faktura PDF została wygenerowana pomyślnie.")
        except Exception as e:
            print(f"Wystąpił błąd podczas generowania faktury PDF: {e}")


