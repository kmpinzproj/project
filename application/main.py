import sys
import os
import sqlite3
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QLabel
from application.view.Formularz_kontaktowy import ContactForm
from application.view.Kreator import Kreator
from application.view.Okno_startowe import OknoStartowe
from application.view.Okno_wymiarów import OknoWymiarow
from application.view.Wybór_bramy import WyborBramy
from PySide6.QtGui import QSurfaceFormat
from pathlib import Path
import os
from application.path import get_resource_path
from application.path import get_persistent_db_path


QApplication.setStyle("Fusion")

class MainApplication(QMainWindow):
    """
    Główna klasa aplikacji zarządzająca widokami oraz inicjalizacją bazy danych.
    """
    VIEW_INDICES = {
        "start": 0,
        "gate_selection": 1,
        "dimension": 2,
        "gate_creator": 3,
        "contact_form": 4,
    }
    DB_FILE = get_persistent_db_path()

    def __init__(self):
        """
        Inicjalizuje główną aplikację.

        Ustawia tytuł okna, inicjalizuje bazę danych i przygotowuje widoki
        oraz połączenia dla aplikacji.
        """
        super().__init__()
        self.gate_creator_view = None
        self.selected_gate_type = None  # Stores the selected gate type
        self.previous_view = None  # Przechowuje poprzedni indeks

        #Initialize DB
        self.initialize_database()

        #Initialize app
        self.setWindowTitle("Main Application")
        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)

        # Initialize QStackedWidget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Add views
        self._initialize_views()

    def resizeEvent(self, event):
        """
        Obsługuje zdarzenie zmiany rozmiaru w celu dostosowania układu aplikacji.

        Args:
            event (QResizeEvent): Zdarzenie zmiany rozmiaru wywołane przez aplikację.
        """
        super().resizeEvent(event)

    def _initialize_views(self):
        """
        Inicjalizuje wszystkie widoki w aplikacji i ustawia ich połączenia.
        """
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
        """
        Ustawia połączenia sygnał-slot dla widoku startowego.
        """
        self.start_view.create_new_button.clicked.connect(
            lambda: self.navigate_to_gate_selection_view()
        )
        self.start_view.open_saved_button.clicked.connect(
            lambda: self.navigate_to_dimension_view(is_opened_project=True)
        )

    def _setup_connections_gate_selection(self):
        """
        Ustawia połączenia sygnał-slot dla widoku wyboru bramy.
        """
        self.gate_selection_view.back_button.clicked.connect(self.navigate_to_start_view)

    def _setup_connections_dimension_view(self):
        """
        Ustawia połączenia sygnał-slot dla widoku wymiarów.
        """
        self.dimension_view.back_button.clicked.connect(self.navigate_back)
        self.dimension_view.accept_button.clicked.connect(self.navigate_to_gate_creator_view)

    def _setup_connections_contact_form(self):
        """
        Ustawia połączenia sygnał-slot dla widoku formularza kontaktowego.
        """
        self.contact_form_view.back_button.clicked.connect(self.navigate_to_gate_creator_view)
        self.contact_form_view.submit_button.clicked.connect(self.navigate_to_start_view)

    def navigate_to_start_view(self):
        """
        Przechodzi do widoku startowego.
        """
        self.start_view.refresh()
        self.previous_view = None
        self.stack.setCurrentIndex(self.VIEW_INDICES["start"])

    def navigate_to_gate_selection_view(self):
        """
        Przechodzi do widoku wyboru bramy.
        """
        self.previous_view = "start"
        self.stack.setCurrentIndex(self.VIEW_INDICES["gate_selection"])

    def navigate_to_dimension_view(self, is_opened_project=False):
        """
        Przechodzi do widoku wymiarów.
        """
        if self.dimension_view:
            self.stack.removeWidget(self.dimension_view)
            self.dimension_view.deleteLater()
            self.dimension_view = None

        self.dimension_view = OknoWymiarow()
        self.stack.insertWidget(self.VIEW_INDICES["dimension"], self.dimension_view)

        # Ustaw poprzedni widok
        if is_opened_project:
            self.previous_view = "start"  # Jeśli projekt został otwarty, cofamy się do startowego
        else:
            self.previous_view = "gate_selection"  # Jeśli stworzono nowy projekt, cofamy się do wyboru bramy

        self.stack.setCurrentIndex(self.VIEW_INDICES["dimension"])
        self._setup_connections_dimension_view()

    def navigate_back(self):
        """
        Powraca do poprzedniego widoku.
        """
        if self.previous_view == "start":
            self.navigate_to_start_view()
        elif self.previous_view == "gate_selection":
            self.navigate_to_gate_selection_view()
        else:
            print("Nie można cofnąć - brak poprzedniego widoku.")

    def navigate_to_gate_creator_view(self):
        """
        Przechodzi do widoku kreatora bramy.
        """
        if self.gate_creator_view:
            self.stack.removeWidget(self.gate_creator_view)
            self.gate_creator_view.deleteLater()
            self.gate_creator_view = None

        # Utwórz nową instancję Kreator
        self.gate_creator_view = Kreator()
        self.stack.insertWidget(self.VIEW_INDICES["gate_creator"], self.gate_creator_view)
        self.previous_index = self.stack.currentWidget()
        self.stack.setCurrentIndex(self.VIEW_INDICES["gate_creator"])
        self._setup_connections_gate_creator()

    def _setup_connections_gate_creator(self):
        """
        Ustawia połączenia sygnał-slot dla widoku kreatora bramy.
        """
        self.gate_creator_view.back_button.clicked.connect(self.navigate_to_dimension_view)
        self.gate_creator_view.contact_button.clicked.connect(self.navigate_to_contact_form_view)

    def navigate_to_contact_form_view(self):
        """
        Przechodzi do widoku formularza kontaktowego.
        """
        # Sprawdzenie, czy użytkownik podał nazwę projektu
        project_name_provided = self.gate_creator_view.prompt_project_name()

        if project_name_provided:  # Jeśli nazwa została poprawnie podana
            self.previous_index = self.stack.currentWidget()
            self.stack.setCurrentIndex(self.VIEW_INDICES["contact_form"])
        else:
            print("Przejście anulowane. Brak nazwy projektu.")

    def initialize_database(self):
        """
        Inicjalizuje połączenie z bazą danych.

        Upewnia się, że plik bazy danych istnieje, i ustanawia niezbędne
        połączenie dla funkcjonalności aplikacji.
        """
        if not os.path.exists(self.DB_FILE):
            print("Baza danych nie istnieje. Tworzenie bazy...")
            try:
                conn = sqlite3.connect(self.DB_FILE)
                path = get_resource_path('models/db-model.sql')
                with open(path, 'r', encoding='utf-8') as file:
                    sql_commands = file.read()
                    conn.executescript(sql_commands)
                conn.close()
                print("Baza danych została utworzona pomyślnie.")
            except (sqlite3.Error, IOError) as e:
                print(f"Błąd podczas tworzenia bazy danych: {e}")
        else:
            print("Baza danych już istnieje.")

def load_stylesheet(app, file_path):
    """
    Ładuje i stosuje arkusz stylów z podanej ścieżki, uwzględniając tryb deweloperski
    i uruchomienie po kompilacji z PyInstaller.

    Args:
        app (QApplication): Instancja aplikacji PySide6.
        file_path (str): Relatywna ścieżka do pliku z arkuszem stylów.
    """
    # Pobierz ścieżkę do pliku z zasobami
    if hasattr(sys, '_MEIPASS'):
        full_path = get_resource_path(file_path)
    else:
        full_path = get_resource_path(file_path).strip("../")

    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as file:
            qss = file.read()
            # Zamień ścieżki w QSS (np. url(...)) na absolutne
            base_path = f"url({get_resource_path("jpg\\tło.jpg")}"
            base_path = base_path.replace("\\", "/")
            qss = qss.replace("url(", base_path)
            app.setStyleSheet(qss)
            print(base_path)
            print(qss)
    else:
        print(f"Plik stylów {full_path} nie istnieje!")

if __name__ == "__main__":
    format = QSurfaceFormat()
    format.setSamples(128)  # Ustaw 8 próbek dla multisamplingu 256
    QSurfaceFormat.setDefaultFormat(format)

    app = QApplication.instance()  # Sprawdź, czy aplikacja już istnieje
    if not app:  # Jeśli nie istnieje, utwórz nową instancję
        app = QApplication(sys.argv)
    load_stylesheet(app, "tools/styles.qss")
    app.setFont(QFont("Arial"))
    main_app = MainApplication()
    main_app.show()
    sys.exit(app.exec())

