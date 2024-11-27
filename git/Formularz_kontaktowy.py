from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QMainWindow, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from button import StyledButton


class ContactForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("ContactForm")  # Ustawiamy nazwę klasy CSS
        self.generate_pdf_button = None
        self.price_calculator_button = None
        self.submit_button = None
        self.back_button = None
        self.comments_input = None
        self.email_input = None
        self.name_input = None
        self.phone_input = None
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)

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
        self.email_input = self._create_form_field("Twój e-mail*", QLineEdit(), form_layout)
        self.phone_input = self._create_form_field("Telefon*", QLineEdit(), form_layout)
        self.comments_input = self._create_form_field("Dodatkowe uwagi", QTextEdit(), form_layout)

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

    from PySide6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy

    def create_buttons_panel(self):
        """Creates the right panel with action buttons spread over half the height."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Dodaj odstęp nad przyciskami, aby zaczęły się od 1/4 wysokości
        layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Dodaj przyciski z odstępami między nimi
        self.generate_pdf_button = StyledButton("Generuj PDF")
        self.price_calculator_button = StyledButton("Kalkulator cen")
        self.submit_button = StyledButton("Wyślij")
        self.back_button = StyledButton("Cofnij")

        layout.addWidget(self.generate_pdf_button)
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.price_calculator_button)
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.submit_button)
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.back_button)

        # Dodaj odstęp pod przyciskami, aby zakończyły się w 3/4 wysokości
        layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return panel