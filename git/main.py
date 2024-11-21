import sys
import os
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLabel

from Formularz_kontaktowy import ContactForm
from Kreator import Kreator
from Okno_startowe import OknoStartowe
from Okno_wymiarów import OknoWymiarow
from Wybór_bramy import WyborBramy

QApplication.setStyle("Fusion")

class MainApplication(QMainWindow):
    VIEW_INDICES = {
        "start": 0,
        "gate_selection": 1,
        "dimension": 2,
        "gate_creator": 3,
        "contact_form": 4,
    }
    DB_FILE = "../resources/project_db.db"

    def __init__(self):
        super().__init__()
        self.gate_creator_view = None
        self.selected_gate_type = None  # Stores the selected gate type

        #Initialize DB
        self.initialize_database()

        self.setWindowTitle("Main Application")
        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)

        # Initialize QStackedWidget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Add views
        self._initialize_views()

    def resizeEvent(self, event):
        """Adjust background image size upon window resizing."""
        super().resizeEvent(event)

    def _initialize_views(self):
        """Creates and adds all views to the QStackedWidget."""
        self.start_view = OknoStartowe()
        self.gate_selection_view = WyborBramy(self.navigate_to_dimension_view)
        self.dimension_view = None
        self.gate_creator_view = None
        self.contact_form_view = ContactForm()

        # Add views to stack
        self.stack.addWidget(self.start_view)
        self.stack.addWidget(self.gate_selection_view)
        self.stack.addWidget(self.contact_form_view)

        # Set up connections for each view
        self._setup_connections_start_view()
        self._setup_connections_gate_selection()
        self._setup_connections_contact_form()

    def _setup_connections_start_view(self):
        """Sets up connections for start view buttons."""
        self.start_view.create_new_button.clicked.connect(self.navigate_to_gate_selection_view)

    def _setup_connections_gate_selection(self):
        """Sets up connections for gate selection view buttons."""
        self.gate_selection_view.back_button.clicked.connect(self.navigate_to_start_view)

    def _setup_connections_dimension_view(self):
        """Sets up connections for dimension view buttons."""
        self.dimension_view.back_button.clicked.connect(self.navigate_to_gate_selection_view)
        self.dimension_view.accept_button.clicked.connect(self.navigate_to_gate_creator_view)

    def _setup_connections_contact_form(self):
        """Sets up connections for contact form view buttons."""
        self.contact_form_view.back_button.clicked.connect(self.navigate_to_gate_creator_view)
        self.contact_form_view.submit_button.clicked.connect(self.navigate_to_start_view)

    def navigate_to_start_view(self):
        self.stack.setCurrentIndex(self.VIEW_INDICES["start"])

    def navigate_to_gate_selection_view(self):
        self.stack.setCurrentIndex(self.VIEW_INDICES["gate_selection"])

    def navigate_to_dimension_view(self):
        if self.dimension_view:
            self.stack.removeWidget(self.dimension_view)
            self.dimension_view.deleteLater()
            self.dimension_view = None

        # Utwórz nową instancję Kreator
        self.dimension_view = OknoWymiarow()
        self.stack.insertWidget(self.VIEW_INDICES["dimension"], self.dimension_view)
        self.stack.setCurrentIndex(self.VIEW_INDICES["dimension"])
        self._setup_connections_dimension_view()

    def navigate_to_gate_creator_view(self):
        """Creates a new instance of Kreator with the selected gate type and configures buttons."""
        # if self.selected_gate_type:
        #     # Usuń istniejący widok kreatora, jeśli już istnieje
        if self.gate_creator_view:
            self.stack.removeWidget(self.gate_creator_view)
            self.gate_creator_view.deleteLater()
            self.gate_creator_view = None

        # Utwórz nową instancję Kreator
        self.gate_creator_view = Kreator(self.selected_gate_type)
        self.stack.insertWidget(self.VIEW_INDICES["gate_creator"], self.gate_creator_view)
        self.stack.setCurrentIndex(self.VIEW_INDICES["gate_creator"])
        self._setup_connections_gate_creator()

    def _setup_connections_gate_creator(self):
        """Sets up connections for the Kreator view buttons."""
        self.gate_creator_view.back_button.clicked.connect(self.navigate_to_dimension_view)
        self.gate_creator_view.contact_button.clicked.connect(self.navigate_to_contact_form_view)

    def navigate_to_contact_form_view(self):
        """Navigates to the contact form view if all required fields in the gate creator are valid."""
        if self.gate_creator_view.validate_fields():
            # Jeśli wszystkie pola są poprawnie wypełnione, przejdź do formularza kontaktowego
            self.stack.setCurrentIndex(self.VIEW_INDICES["contact_form"])
            print("Przejście do widoku formularza kontaktowego.")
        else:
            # Jeśli walidacja nie powiodła się, wyświetl komunikat w konsoli
            print("Nie wszystkie wymagane opcje zostały wybrane!")

    def initialize_database(self):
        """Initializes the database if it does not already exist."""
        if not os.path.exists(self.DB_FILE):
            print("Baza danych nie istnieje. Tworzenie bazy...")
            try:
                conn = sqlite3.connect(self.DB_FILE)
                with open('../models/db-model.sql', 'r', encoding='utf-8') as file:
                    sql_commands = file.read()
                    conn.executescript(sql_commands)
                conn.close()
                print("Baza danych została utworzona pomyślnie.")
            except (sqlite3.Error, IOError) as e:
                print(f"Błąd podczas tworzenia bazy danych: {e}")
        else:
            print("Baza danych już istnieje.")

def load_stylesheet(app, file_path):
    """Ładuje plik stylów CSS i stosuje go do aplikacji."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            app.setStyleSheet(file.read())
    else:
        print(f"Plik stylów {file_path} nie istnieje!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app, "styles.qss")
    app.setFont(QFont("Arial"))
    main_app = MainApplication()
    main_app.show()
    sys.exit(app.exec())
