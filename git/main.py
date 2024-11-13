import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
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

        # Dodany atrybut do przechowania wybranego typu bramy
        self.selected_gate_type = None

        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)

        self.original_pixmap = QPixmap("tło.jpg")  # Wczytaj obraz oryginalny
        self.resize_background()

        # Initialize QStackedWidget and set it as central widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initialize and add views
        self._initialize_views()
        self._add_views_to_stack()

        # Set up connections for buttons
        self._setup_connections()

    def resizeEvent(self, event):
        """Dostosowuje obraz tła do rozmiaru okna przy zmianie jego rozmiaru."""
        super().resizeEvent(event)
        self.resize_background()

    def resize_background(self):
        """Skaluje tło, aby dopasować je do rozmiaru okna, zachowując proporcje i przycinając nadmiar."""
        # Ustaw QLabel na pełny rozmiar okna
        self.background_label.setGeometry(self.rect())

        # Oblicz proporcje okna i obrazu
        window_ratio = self.width() / self.height()
        pixmap_ratio = self.original_pixmap.width() / self.original_pixmap.height()

        # Dopasowanie szerokości lub wysokości, zachowując proporcje obrazu
        if window_ratio > pixmap_ratio:
            # Okno jest szersze niż obraz - dostosuj szerokość
            scaled_pixmap = self.original_pixmap.scaledToHeight(self.height(), Qt.SmoothTransformation)
        else:
            # Okno jest wyższe niż obraz - dostosuj wysokość
            scaled_pixmap = self.original_pixmap.scaledToWidth(self.width(), Qt.SmoothTransformation)

        # Ustaw przeskalowany obraz jako tło
        self.background_label.setPixmap(scaled_pixmap)

    def _initialize_views(self):
        """Initializes all views used in the application."""
        self.start_view = OknoStartowe()
        self.gate_selection_view = WyborBramy(self.set_selected_gate_type)
        self.dimension_view = OknoWymiarow()
        self.gate_creator_view = Kreator("Brama segmentowa")
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
        """Otwiera kreator z odpowiednimi opcjami na podstawie wybranego typu bramy."""
        if self.selected_gate_type:
            # Tworzy widok Kreatora na podstawie wybranego typu bramy
            self.gate_creator_view = Kreator(self.selected_gate_type)
            self.stack.addWidget(self.gate_creator_view)  # Dodaje widok kreatora do stosu widoków
            self.stack.setCurrentWidget(self.gate_creator_view)  # Przechodzi do widoku kreatora

            self.gate_creator_view.back_button.clicked.connect(self.navigate_to_dimension_view)
            self.gate_creator_view.save_button.clicked.connect(self.navigate_to_contact_form_view)

    def navigate_to_contact_form_view(self):
        """Navigates to the contact form view."""
        self.stack.setCurrentIndex(self.CONTACT_FORM_VIEW)

    # Nowe metody dla wyboru i otwarcia kreatora z wybranym typem bramy
    def set_selected_gate_type(self, gate_type):
        """Zapisuje wybrany typ bramy."""
        self.selected_gate_type = gate_type
        self.stack.setCurrentWidget(self.dimension_view)  # Przechodzi do Okno_wymiarów

    def open_gate_creator(self):
        """Inicjalizuje kreator z wybranym typem bramy po wprowadzeniu wymiarów."""
        if self.selected_gate_type:
            self.gate_creator_view = Kreator(self.selected_gate_type)
            self.gate_creator_view.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApplication()
    main_app.show()
    sys.exit(app.exec())