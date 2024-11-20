from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow, QSpacerItem, QSizePolicy, QWidget,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHeaderView
)
from PySide6.QtGui import QFont, QPixmap
from button import StyledButton
from git.DatabaseManager import DatabaseManager
import json
import os


class OknoStartowe(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)  # Ustawienie minimalnego rozmiaru okna

        # Ustawienia główne i UI
        self.selected_row = None  # Zmienna przechowująca ID zaznaczonego projektu
        self.db_manager = DatabaseManager()  # Menedżer bazy danych
        self._setup_ui()
        self._load_project_files()

    def _setup_ui(self):
        """Konfiguruje główny layout i dzieli na panele lewe i prawe."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Tworzenie paneli lewego i prawego
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        main_layout.setStretch(0, 2)  # Lewy panel
        main_layout.setStretch(1, 3)  # Prawy panel

    def _create_left_panel(self):
        """Tworzy lewy panel z przyciskami do zarządzania projektami."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Dodanie odstępów
        self._add_spacer(left_layout)

        # Przycisk tworzenia i otwierania projektów
        self.create_new_button = StyledButton("Stwórz nowy")
        self.open_saved_button = StyledButton("Otwórz zapisany")

        # Podłącz akcje przycisków
        self.create_new_button.clicked.connect(self.clear_selected_options)
        self.open_saved_button.clicked.connect(self.open_selected_project)

        left_layout.addWidget(self.create_new_button)
        left_layout.addWidget(self.open_saved_button)

        # Dodatkowy odstęp dla wyśrodkowania
        self._add_spacer(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return left_widget

    def _create_right_panel(self):
        """Tworzy prawy panel z tabelką projektów."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Tabela z projektami
        self.project_table = QTableWidget()
        self.project_table.setColumnCount(3)  # Trzy kolumny: obraz, nazwa, data
        self.project_table.setHorizontalHeaderLabels(["Typ", "Nazwa Projektu", "Data Zapisu"])
        self.project_table.setSelectionBehavior(QTableWidget.SelectRows)  # Zaznaczanie całych wierszy
        self.project_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Wyłącz edytowanie pól
        self.project_table.setShowGrid(False)  # Ukrycie siatki
        self.project_table.verticalHeader().setVisible(False)  # Ukrycie nagłówków wierszy
        self.project_table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                color: white;
            }
            QHeaderView::section {
                background-color: #333333;
                color: white;
                border: 1px solid #444444;
                padding: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item:selected {
                background-color: rgba(100, 100, 100, 0.8);
                color: red;
            }
        """)

        # Konfiguracja nagłówków
        header = self.project_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Kolumna z obrazem dopasowana do zawartości
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Kolumna z nazwą projektu dynamiczna
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Kolumna z datą dopasowana do zawartości

        # Obsługa wyboru wiersza
        self.project_table.itemSelectionChanged.connect(self._handle_row_selection)

        right_layout.addWidget(self.project_table)
        return right_widget

    @staticmethod
    def _add_spacer(layout):
        """Dodaje odstęp pionowy do ustawienia pozycji elementów."""
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _load_project_files(self):
        """Ładuje projekty z bazy danych do tabelki z obrazem JPG, nazwą i datą zapisu."""
        self.project_table.clearContents()
        projects = self.db_manager.list_projects()
        image_path = "../jpg/icon.png"  # Ścieżka do domyślnego obrazu

        if projects:
            self.project_table.setRowCount(len(projects))

            for row, project in enumerate(projects):
                project_name = project[1]  # Nazwa projektu (kolumna 1)
                project_date = project[2]  # Data zapisu (kolumna 2)

                # Dodanie obrazu do pierwszej kolumny
                image_label = QLabel()
                pixmap = QPixmap(image_path)
                scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
                image_label.setAlignment(Qt.AlignCenter)  # Wyśrodkowanie obrazu
                self.project_table.setCellWidget(row, 0, image_label)
                self.project_table.setRowHeight(row, 80)  # Dopasowanie wysokości wiersza

                # Dodanie nazwy projektu
                name_item = QTableWidgetItem(project_name)
                name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                name_item.setTextAlignment(Qt.AlignCenter)  # Wyśrodkowanie nazwy
                self.project_table.setItem(row, 1, name_item)

                # Dodanie daty zapisu
                date_item = QTableWidgetItem(project_date)
                date_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                date_item.setTextAlignment(Qt.AlignCenter)  # Wyśrodkowanie daty
                self.project_table.setItem(row, 2, date_item)
        else:
            self.project_table.setRowCount(1)
            empty_item = QTableWidgetItem("Brak zapisanych projektów")
            empty_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            empty_item.setTextAlignment(Qt.AlignCenter)  # Wyśrodkowanie komunikatu
            self.project_table.setItem(0, 1, empty_item)

    def clear_selected_options(self):
        """Clears the contents of the JSON file or creates it if it doesn't exist."""
        file_path = "selected_options.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump({}, file, ensure_ascii=False, indent=4)
            print(f"Plik {file_path} został utworzony lub wyczyszczony.")
        except Exception as e:
            print(f"Wystąpił błąd podczas operacji na pliku: {e}")

    def open_selected_project(self):
        """Czyści opcje i pobiera dane zaznaczonego projektu na podstawie nazwy projektu oraz powiązanej bramy."""
        self.clear_selected_options()

        if self.selected_row is not None:
            # Pobranie nazwy projektu z tabeli
            project_name_item = self.project_table.item(self.selected_row, 1)  # Nazwa projektu jest w kolumnie 1
            print(project_name_item)
            if project_name_item:
                project_name = project_name_item.text()
                # Pobranie danych projektu i powiązanej bramy z bazy na podstawie nazwy projektu
                project_data = self.db_manager.get_project_by_name(project_name)
                if project_data:
                    print(f"Wybrany projekt: {project_data['projekt']}")
                    print(f"Powiązana brama: {project_data['brama']}")
                else:
                    print("Nie udało się pobrać danych projektu.")
            else:
                print("Nie można odczytać nazwy projektu z tabeli.")
        else:
            print("Nie zaznaczono żadnego projektu.")

    def _handle_row_selection(self):
        """Obsługuje zaznaczanie wiersza w tabeli."""
        selected_items = self.project_table.selectedItems()
        if selected_items:
            row = self.project_table.row(selected_items[0])
            self.selected_row = row + 1  # Zakładam, że ID projektu odpowiada numerowi wiersza (zaczyna od 1)
        else:
            self.selected_row = None
