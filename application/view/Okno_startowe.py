from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QSpacerItem, QSizePolicy, QWidget,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHeaderView
)
from PySide6.QtGui import QPixmap
from application.tools.button import StyledButton
from application.DatabaseManager import DatabaseManager
import json
from application.tools.path import get_resource_path


class OknoStartowe(QMainWindow):
    """
    Klasa reprezentująca ekran początkowy aplikacji.
    """
    def __init__(self):
        """
        Inicjalizuje okno startowe aplikacji.

        Tworzy i konfiguruje interfejs użytkownika oraz przygotowuje niezbędne elementy.
        """
        super().__init__()
        self.setObjectName("OknoStartowe")  # Dodanie identyfikatora dla stylów
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)

        self.selected_row = None
        self.db_manager = DatabaseManager()
        self._setup_ui()
        self.refresh()  # Odśwież zawartość przy pierwszym uruchomieniu

    def _setup_ui(self):
        """
        Konfiguruje interfejs użytkownika.

        Tworzy główny układ aplikacji z lewym i prawym panelem oraz dodaje
        podstawowe widżety.
        """
        central_widget = QWidget(self)
        central_widget.setObjectName("oknoStartoweWindow")
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        main_layout.setStretch(0, 2)
        main_layout.setStretch(1, 3)

    def _create_left_panel(self):
        """
        Tworzy lewy panel w oknie startowym.

        Panel zawiera przyciski do tworzenia nowych projektów, otwierania zapisanych
        oraz usuwania projektów.
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self._add_spacer(left_layout)

        self.create_new_button = StyledButton("Stwórz nowy")
        self.open_saved_button = StyledButton("Otwórz zapisany")
        self.delete_button = StyledButton("Usuń projekt")  # Nowy przycisk
        self.open_saved_button.setEnabled(False)  # Domyślnie wyłączony
        self.delete_button.setEnabled(False)  # Wyłączony domyślnie

        self.create_new_button.clicked.connect(self.clear_selected_options)
        self.open_saved_button.clicked.connect(self.open_selected_project)
        self.delete_button.clicked.connect(self.delete_selected_project)  # Połączenie z metodą

        left_layout.addWidget(self.create_new_button)
        left_layout.addWidget(self.open_saved_button)
        left_layout.addWidget(self.delete_button)  # Dodanie przycisku

        self._add_spacer(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return left_widget

    def _create_right_panel(self):
        """
        Tworzy prawy panel w oknie startowym.

        Panel zawiera tabelę listę utworzonych projektów.
        """
        right_widget = QWidget()
        right_widget.setObjectName("projectTablePanel")
        right_layout = QVBoxLayout(right_widget)

        self.project_table = QTableWidget()
        self.project_table.setObjectName("projectTable")
        self.project_table.setColumnCount(3)
        self.project_table.setHorizontalHeaderLabels(["Typ", "Nazwa Projektu", "Data Zapisu"])
        self.project_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.project_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.project_table.setShowGrid(False)
        self.project_table.verticalHeader().setVisible(False)

        header = self.project_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.project_table.itemSelectionChanged.connect(self._handle_row_selection)

        right_layout.addWidget(self.project_table)
        return right_widget

    def _handle_row_selection(self):
        """
        Obsługuje wybór wiersza w tabeli projektów.

        Włącza przyciski "Otwórz zapisany" i "Usuń projekt", gdy wiersz w tabeli jest zaznaczony.
        """
        selected_items = self.project_table.selectedItems()
        if selected_items:
            self.selected_row = self.project_table.row(selected_items[0]) + 1
            self.open_saved_button.setEnabled(True)  # Aktywuj przycisk otwierania
            self.delete_button.setEnabled(True)  # Aktywuj przycisk usuwania
        else:
            self.selected_row = None
            self.open_saved_button.setEnabled(False)  # Wyłącz przycisk otwierania
            self.delete_button.setEnabled(False)  # Wyłącz przycisk usuwania

    def open_selected_project(self):
        """
        Otwiera wybrany projekt z bazy danych.

        Wczytuje dane projektu i zapisuje je do pliku JSON, który będzie używany w kolejnych widokach.
        """
        self.clear_selected_options()

        selected_items = self.project_table.selectedItems()

        selected_row = self.project_table.row(selected_items[0])
        project_name_item = self.project_table.item(selected_row, 1)
        if project_name_item:
            project_name = project_name_item.text()
            try:
                output_file = get_resource_path("resources/selected_options.json")
                self.db_manager.load_project_to_json(project_name, output_file)
            except Exception as e:
                print(f"Błąd podczas zapisywania projektu do JSON: {e}")

    def delete_selected_project(self):
        """
        Usuwa wybrany projekt z bazy danych.

        Wywołuje funkcję `test` z klasy `DatabaseManager`.
        """
        selected_items = self.project_table.selectedItems()

        if selected_items:
            selected_row = self.project_table.row(selected_items[0])
            project_name_item = self.project_table.item(selected_row, 1)

            if project_name_item:
                project_name = project_name_item.text()
                try:
                    self.db_manager.delete_project_by_name(project_name)  # Wywołanie funkcji `test`
                    self.refresh()  # Odświeżenie tabeli po usunięciu
                    print(f"Projekt '{project_name}' został usunięty.")
                except Exception as e:
                    print(f"Błąd podczas usuwania projektu: {e}")

    def refresh(self):
        """
        Odświeża dane w tabeli projektów.

        Ładuje listę projektów z bazy danych i wyświetla je w tabeli.
        """
        self._load_project_files()

    def _load_project_files(self):
        """
        Ładuje listę projektów z bazy danych i uzupełnia tabelę.

        Pobiera dane projektów, takie jak nazwa i data, i wyświetla je w odpowiednich komórkach.
        """
        self.project_table.clearContents()

        projects = self.db_manager.list_projects()
        image_path = get_resource_path("jpg/icon.png")

        if projects:
            self.project_table.setRowCount(len(projects))

            for row, project in enumerate(projects):
                project_name = project[1]
                project_date = project[2]
                project_type = project[3]

                image_path = get_resource_path(f"jpg/{project_type}.png")

                image_label = QLabel()
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
                image_label.setAlignment(Qt.AlignCenter)
                self.project_table.setCellWidget(row, 0, image_label)
                self.project_table.setRowHeight(row, 80)

                name_item = QTableWidgetItem(project_name)
                name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.project_table.setItem(row, 1, name_item)

                date_item = QTableWidgetItem(project_date)
                date_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                date_item.setTextAlignment(Qt.AlignCenter)
                self.project_table.setItem(row, 2, date_item)

    @staticmethod
    def clear_selected_options():
        """
        Czyści plik z zapisanymi opcjami projektu.

        Zapisuje pusty słownik do pliku JSON, usuwając wszystkie poprzednie dane.
        """
        file_path = get_resource_path("resources/selected_options.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump({}, file, ensure_ascii=False, indent=4)
            print(f"Plik {file_path} został wyczyszczony.")
        except Exception as e:
            print(f"Błąd podczas czyszczenia pliku: {e}")

    @staticmethod
    def _add_spacer(layout):
        """
        Dodaje pustą przestrzeń do układu.

        Args:
            layout (QLayout): Układ, do którego zostanie dodany odstęp.
        """
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))