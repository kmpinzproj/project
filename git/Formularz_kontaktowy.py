from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QMainWindow, QSizePolicy
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from button import StyledButton
from Widget3D import OpenGLWidget  # Import widżetu 3D
import os

class ContactForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("ContactForm")  # Ustawiamy nazwę klasy CSS
        self.submit_button = None
        self.back_button = None
        self.comments_input = None
        self.email_input = None
        self.name_input = None
        self.phone_input = None
        self.opengl_widget = None  # Widżet 3D
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
        view_panel = self.create_view_panel()  # Utwórz widok z widżetem 3D

        main_layout.addWidget(navigation_panel)
        main_layout.addWidget(view_panel)

        main_layout.setStretch(0, 2)  # Navigation panel
        main_layout.setStretch(1, 2)  # View panel

    def create_navigation_panel(self):
        """Creates the left panel with contact form fields and action buttons."""
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

        # Button layout centered at the bottom
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        self.back_button = StyledButton("Cofnij")
        self.submit_button = StyledButton("Wyślij")

        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.submit_button)

        # Add layouts to the main panel layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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

    def create_view_panel(self):
        """Creates the right panel with a 3D view."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Ścieżka do modelu 3D
        obj_file = "../generator/model.obj"

        if os.path.exists(obj_file):
            # Tworzenie widżetu OpenGL z załadowanym modelem
            self.opengl_widget = OpenGLWidget(obj_file)

            # Ograniczenie wysokości widoku 3D
            self.opengl_widget.setFixedHeight(250)  # Ustawienie stałej wysokości

            # Dodanie widżetu do układu
            layout.addWidget(self.opengl_widget)
        else:
            # Placeholder jeśli model nie istnieje
            placeholder_label = QLabel("Widok 3D: Nie znaleziono modelu.")
            placeholder_label.setAlignment(Qt.AlignCenter)
            placeholder_label.setFont(QFont("Arial", 12, QFont.Bold))
            layout.addWidget(placeholder_label)

        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return panel