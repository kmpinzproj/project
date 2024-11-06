from PySide6.QtWidgets import (
    QMainWindow,QSpacerItem,QSizePolicy, QWidget,
    QListWidget, QVBoxLayout, QHBoxLayout
)
from button import StyledButton


class OknoStartowe(QMainWindow):
    # Constants for window and panel dimensions
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    LEFT_PANEL_WIDTH = 400

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        # Setup UI
        self._setup_ui()

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

    def _create_left_panel(self):
        """Creates the left panel with buttons for creating or opening projects."""
        left_widget = QWidget()
        left_widget.setFixedWidth(self.LEFT_PANEL_WIDTH)
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

        return left_widget

    def _create_right_panel(self):
        """Creates the right panel with a project list."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Project list widget
        self.project_list = QListWidget()
        self.project_list.addItem("Lista zapisanych projektów")  # Placeholder item

        right_layout.addWidget(self.project_list)

        return right_widget

    def _add_spacer(self, layout):
        """Adds a vertical spacer to adjust vertical positioning of content."""
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
