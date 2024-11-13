from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow, QSpacerItem, QSizePolicy, QWidget,
    QListWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem
)

from CustomListWidgetItem import CustomListWidgetItem
from button import StyledButton


class OknoStartowe(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)  # Ustawienie minimalnego rozmiaru okna

        # Ustawienia główne i UI
        self.selected_item = None
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
        main_layout.setStretch(1, 2)  # Prawy panel

    def _create_left_panel(self):
        """Tworzy lewy panel z przyciskami do zarządzania projektami."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Dodanie odstępów
        self._add_spacer(left_layout)

        # Przycisk tworzenia i otwierania projektów
        self.create_new_button = StyledButton("Stwórz nowy")
        self.open_saved_button = StyledButton("Otwórz zapisany")
        left_layout.addWidget(self.create_new_button)
        left_layout.addWidget(self.open_saved_button)

        # Dodatkowy odstęp dla wyśrodkowania
        self._add_spacer(left_layout)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return left_widget

    def _create_right_panel(self):
        """Tworzy prawy panel z listą projektów w trybie ikon."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Lista projektów w trybie ikon
        self.project_list = QListWidget()
        self._configure_project_list_style()
        self.project_list.itemClicked.connect(self._toggle_item_selection)
        right_layout.addWidget(self.project_list)
        self.project_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return right_widget

    def _configure_project_list_style(self):
        """Ustawienia stylu i trybu dla QListWidget z projektami."""
        self.project_list.setViewMode(QListWidget.IconMode)
        self.project_list.setIconSize(QSize(64, 64))
        self.project_list.setSpacing(10)
        self.project_list.setSelectionMode(QListWidget.SingleSelection)
        self.project_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(80, 80, 80, 0.8);
                border: none;
            }
            QListWidget::item:selected {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                selection-background-color: transparent;
            }
        """)

    @staticmethod
    def _add_spacer(layout):
        """Dodaje odstęp pionowy do ustawienia pozycji elementów."""
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def resizeEvent(self, event):
        """Dostosowuje rozmiar siatki ikon dynamicznie przy zmianie rozmiaru."""
        super().resizeEvent(event)
        self._adjust_grid_size()

    def _adjust_grid_size(self):
        """Dostosowuje rozmiar siatki elementów QListWidget na podstawie dostępnej szerokości."""
        available_width = self.project_list.viewport().width()
        icon_width = self.project_list.iconSize().width()
        spacing = self.project_list.spacing()
        items_per_row = max(1, available_width // (icon_width + spacing))
        self.project_list.setGridSize(QSize(available_width // items_per_row, icon_width + 30))

    def _load_project_files(self):
        """Ładuje pliki projektów .txt z katalogu 'zapisane_projekty' do listy projektów."""
        base_dir = Path(__file__).resolve().parent
        projects_dir = base_dir / '..' / 'zapisane_projekty'
        projects_dir.mkdir(exist_ok=True)

        self.project_list.clear()
        project_files = list(projects_dir.glob("*.txt"))
        icon_path = "icon.png"  # Ścieżka do ikony

        if project_files:
            for file_path in project_files:
                custom_widget = CustomListWidgetItem(file_path.stem, icon_path)
                list_item = QListWidgetItem(self.project_list)
                list_item.setSizeHint(custom_widget.sizeHint())
                self.project_list.addItem(list_item)
                self.project_list.setItemWidget(list_item, custom_widget)
        else:
            list_item = QListWidgetItem("Brak zapisanych projektów")
            list_item.setFlags(Qt.NoItemFlags)
            self.project_list.addItem(list_item)

    def _toggle_item_selection(self, item):
        """Przełącza stan zaznaczenia elementu i stosuje czerwoną ramkę dla zaznaczonego."""
        widget = self.project_list.itemWidget(item)
        if self.selected_item == widget:
            widget.set_selected(False)
            self.selected_item = None
        else:
            if self.selected_item:
                self.selected_item.set_selected(False)
            widget.set_selected(True)
            self.selected_item = widget