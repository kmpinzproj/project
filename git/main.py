import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from Okno_startowe import OknoStartowe
from Okno_wymiarów import OknoWymiarow
from Wybór_bramy import WyborBramy
from Kreator import Kreator
from Formularz_kontaktowy import ContactForm

class MainApplication(QMainWindow):
    # View indices
    START_VIEW = 0
    GATE_SELECTION_VIEW = 1
    DIMENSION_VIEW = 2
    GATE_CREATOR_VIEW = 3
    CONTACT_FORM_VIEW = 4

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application")

        # Initialize QStackedWidget and set it as central widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initialize and add views
        self._initialize_views()
        self._add_views_to_stack()

        # Set up connections for buttons
        self._setup_connections()

    def _initialize_views(self):
        """Initializes all views used in the application."""
        self.start_view = OknoStartowe()
        self.dimension_view = OknoWymiarow()
        self.gate_selection_view = WyborBramy()
        self.gate_creator_view = Kreator()
        self.connect_form_view = ContactForm()

    def _add_views_to_stack(self):
        """Adds all views to the QStackedWidget stack."""
        self.stack.addWidget(self.start_view)
        self.stack.addWidget(self.gate_selection_view)
        self.stack.addWidget(self.dimension_view)
        self.stack.addWidget(self.gate_creator_view)
        self.stack.addWidget(self.connect_form_view)

    def _setup_connections(self):
        """Sets up button connections for view navigation."""
        # Start view button
        self.start_view.create_new_button.clicked.connect(self.navigate_to_gate_selection_view)

        # Gate selection view buttons
        self.gate_selection_view.back_button.clicked.connect(self.navigate_to_start_view)
        self.gate_selection_view.accept_button.clicked.connect(self.navigate_to_dimension_view)

        # Dimension view buttons
        self.dimension_view.back_button.clicked.connect(self.navigate_to_gate_selection_view)
        self.dimension_view.accept_button.clicked.connect(self.navigate_to_gate_creator_view)

        # Gate creator view buttons
        self.gate_creator_view.back_button.clicked.connect(self.navigate_to_dimension_view)
        self.gate_creator_view.save_button.clicked.connect(self.navigate_to_contact_form_view)

        # Contact form view buttons
        self.connect_form_view.back_button.clicked.connect(self.navigate_to_gate_creator_view)
        self.connect_form_view.submit_button.clicked.connect(self.navigate_to_start_view)

    # Navigation methods
    def navigate_to_start_view(self):
        """Navigates to the start view."""
        self.stack.setCurrentIndex(self.START_VIEW)

    def navigate_to_gate_selection_view(self):
        """Navigates to the gate selection view."""
        self.stack.setCurrentIndex(self.GATE_SELECTION_VIEW)

    def navigate_to_dimension_view(self):
        """Navigates to the dimension view."""
        self.stack.setCurrentIndex(self.DIMENSION_VIEW)

    def navigate_to_gate_creator_view(self):
        """Navigates to the gate creator view."""
        self.stack.setCurrentIndex(self.GATE_CREATOR_VIEW)

    def navigate_to_contact_form_view(self):
        """Navigates to the contact form view."""
        self.stack.setCurrentIndex(self.CONTACT_FORM_VIEW)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApplication()
    main_app.show()
    sys.exit(app.exec())