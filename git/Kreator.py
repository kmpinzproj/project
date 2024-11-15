from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from Rozwijane_menu import ScrollableMenu
from button import StyledButton

class Kreator(QMainWindow):
    LEFT_PANEL_WIDTH = 400
    OPENGL_WIDGET_MIN_SIZE = 400  # Minimum size for OpenGL widget

    def __init__(self, gate_type):
        super().__init__()
        self.gate_type = gate_type
        self.setWindowTitle(f"Kreator - {self.gate_type}")
        self.setGeometry(100, 100, 834, 559)
        self.setMinimumSize(834, 559)

        # Initialize UI
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the main layout and divides it into left and right panels."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Remove margins and spacing to avoid horizontal scrolling
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create panels
        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        # Add panels to the main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

    def _create_left_panel(self):
        """Creates the left panel with the scrollable menu based on gate type."""
        left_widget = QWidget()
        left_widget.setFixedWidth(self.LEFT_PANEL_WIDTH)
        left_layout = QVBoxLayout(left_widget)

        # Remove margins and spacing for the scrollable menu
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Add scrollable navigation menu
        navigation_menu = ScrollableMenu(self.gate_type)
        left_layout.addWidget(navigation_menu)

        return left_widget

    def _create_right_panel(self):
        """Creates the right panel with OpenGL widget and navigation buttons."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # OpenGL widget for 3D visualization
        open_gl_widget = self._create_opengl_widget()
        right_layout.addWidget(open_gl_widget)

        # Navigation buttons at the bottom
        buttons_widget = self._create_navigation_buttons()
        right_layout.addWidget(buttons_widget)

        return right_widget

    def _create_opengl_widget(self):
        """Creates and configures the OpenGL widget."""
        open_gl_widget = QOpenGLWidget()
        open_gl_widget.setObjectName("openGLWidget")
        open_gl_widget.setMinimumSize(self.OPENGL_WIDGET_MIN_SIZE, self.OPENGL_WIDGET_MIN_SIZE)
        return open_gl_widget

    def _create_navigation_buttons(self):
        """Creates a widget with 'Back' and 'Save' buttons."""
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        # Create Back and Save buttons
        self.back_button = StyledButton("Cofnij")
        self.save_button = StyledButton("Zapisz")

        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.save_button)

        # Remove margins and spacing for navigation buttons
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        return buttons_widget