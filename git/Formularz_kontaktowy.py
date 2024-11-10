from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QFormLayout, QMainWindow, QSizePolicy
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from button import StyledButton


class ContactForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)  # Ustawienie minimalnego rozmiaru okna

        # Setup the main interface
        self.setup_ui()

    def setup_ui(self):
        # Central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left and Right panels
        navigation_panel = self.create_navigation_panel()
        view_panel = self.create_view_panel()

        main_layout.addWidget(navigation_panel)
        main_layout.addWidget(view_panel)

        # Ustaw rozciąganie, aby lewy panel był szerszy
        main_layout.setStretch(0, 2)
        main_layout.setStretch(1, 2)

    def create_navigation_panel(self):
        # Define navigation panel components
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title and subtitle
        title_label = QLabel("Segmentowe. Wyślij zapytanie.")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        subtitle_label = QLabel("Wypełnij formularz kontaktowy. Nasz konsultant skontaktuje się z Tobą.")

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        # Nowy layout dla formularza z etykietami nad polami
        form_layout = QVBoxLayout()

        # Funkcja pomocnicza do tworzenia pól z etykietami nad nimi
        def create_field(label_text, widget):
            field_layout = QVBoxLayout()
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 14))
            field_layout.addWidget(label)
            field_layout.addWidget(widget)
            return field_layout

        # Create input fields
        name_input = QLineEdit()
        email_input = QLineEdit()
        phone_input = QLineEdit()
        comments_input = QTextEdit()

        # Ustawienie polityki rozmiaru, aby pola formularza były responsywne
        name_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        email_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        phone_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        comments_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Dodanie pól z etykietami nad nimi do układu formularza
        form_layout.addLayout(create_field("Imię i nazwisko*", name_input))
        form_layout.addLayout(create_field("Twój e-mail*", email_input))
        form_layout.addLayout(create_field("Telefon*", phone_input))
        form_layout.addLayout(create_field("Dodatkowe uwagi", comments_input))

        # Button layout centered at the bottom
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        # Define buttons
        self.back_button = StyledButton("Cofnij")
        self.submit_button = StyledButton("Wyślij")

        # Add buttons to the button layout
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.submit_button)

        # Adding layouts and widgets to the left layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)  # Add centered button layout

        # Ustawienie polityki rozmiaru dla panelu nawigacyjnego
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return panel

        # Define buttons
        self.back_button = StyledButton("Cofnij")
        self.submit_button = StyledButton("Wyślij")

        # Add buttons to the button layout
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.submit_button)

        # Adding layouts and widgets to the left layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)  # Add centered button layout

        # Ustawienie polityki rozmiaru dla panelu nawigacyjnego
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return panel

    def create_view_panel(self):
        # Define view panel (for 3D view) components here
        panel = QWidget()
        layout = QVBoxLayout(panel)

        placeholder_label = QLabel("Widok 3D (Placeholder)")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setFont(QFont("Arial", 12, QFont.Bold))

        layout.addWidget(placeholder_label)

        # Ustawienie polityki rozmiaru, aby panel widoku 3D był elastyczny
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return panel