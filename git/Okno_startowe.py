import os
from PySide6.QtWidgets import (
    QMainWindow, QSpacerItem, QSizePolicy, QWidget,
    QListWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem
)
from button import StyledButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from CustomListWidgetItem import CustomListWidgetItem


class OknoStartowe(QMainWindow):
    # Constants for window and panel dimensions
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Setup UI
        self._setup_ui()
        # Load project files into the project list
        self._load_project_files()

        # Track selected item to toggle selection
        self.selected_item = None

    def _setup_ui(self):
        """Configures the main layout and divides it into left and right panels."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Create and add left and right panels
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        # Ustaw rozciąganie: lewy panel będzie bardziej sztywny, prawy bardziej elastyczny
        main_layout.setStretch(0, 2)  # Lewy panel
        main_layout.setStretch(1, 2)  # Prawy panel

    def _create_left_panel(self):
        """Creates the left panel with buttons for creating or opening projects."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Spacer to push content lower
        self._add_spacer(left_layout)

        # Buttons for creating and opening projects
        self.create_new_button = StyledButton("Stwórz nowy")
        self.open_saved_button = StyledButton("Otwórz zapisany")

        left_layout.addWidget(self.create_new_button)
        left_layout.addWidget(self.open_saved_button)

        # Spacer to keep buttons vertically centered
        self._add_spacer(left_layout)

        # Ustaw politykę rozmiaru na Expanding, aby był elastyczny
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return left_widget

    def _create_right_panel(self):
        """Creates the right panel with a project list in icon mode."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Project list widget in icon mode
        self.project_list = QListWidget()
        self.project_list.setViewMode(QListWidget.IconMode)  # Icon mode
        self.project_list.setIconSize(QSize(64, 64))  # Set icon size
        self.project_list.setSpacing(10)  # Space between icons
        self.project_list.setSelectionMode(QListWidget.SingleSelection)  # Single selection only

        # Remove default blue selection highlight
        self.project_list.setStyleSheet("""
            QListWidget::item:selected {
                background-color: transparent;  /* Usuwa niebieskie tło przy zaznaczeniu */
                border: none;                   /* Usuwa domyślną ramkę */
            }
            QListWidget::item {
                selection-background-color: transparent;  /* Usuwa domyślne podświetlenie */
            }
        """)

        # Connect click event to custom selection logic
        self.project_list.itemClicked.connect(self._toggle_item_selection)

        right_layout.addWidget(self.project_list)

        # Ustaw politykę rozmiaru, aby projekt list mógł się elastycznie rozszerzać
        self.project_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        return right_widget

    def _add_spacer(self, layout):
        """Adds a vertical spacer to adjust vertical positioning of content."""
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _load_project_files(self):
        """Loads .txt project files from the 'project/zapisane_projekty' directory into the project list."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        projects_dir = os.path.join(base_dir, '..', 'zapisane_projekty')

        if not os.path.exists(projects_dir):
            os.makedirs(projects_dir)

        # Wyczyść listę projektów
        self.project_list.clear()

        # List all .txt files in the projects directory
        project_files = [f for f in os.listdir(projects_dir) if f.endswith(".txt")]

        # Dodaj każdy plik jako element z ikoną
        icon_path = "icon.png"  # Zmień na rzeczywistą ścieżkę do ikony
        if project_files:
            for file_name in project_files:
                custom_widget = CustomListWidgetItem(file_name, icon_path)
                list_item = QListWidgetItem(self.project_list)
                list_item.setSizeHint(custom_widget.sizeHint())
                self.project_list.addItem(list_item)
                self.project_list.setItemWidget(list_item, custom_widget)
        else:
            list_item = QListWidgetItem("Brak zapisanych projektów")
            list_item.setFlags(Qt.NoItemFlags)  # Make it unselectable
            self.project_list.addItem(list_item)

    def _toggle_item_selection(self, item):
        """Toggle selection state and apply red border for selected item."""
        widget = self.project_list.itemWidget(item)

        if self.selected_item == widget:  # Item is already selected
            # Deselect the item
            widget.set_selected(False)
            self.selected_item = None
        else:
            # Deselect the previous item if any
            if self.selected_item:
                self.selected_item.set_selected(False)

            # Select the new item
            widget.set_selected(True)
            self.selected_item = widget