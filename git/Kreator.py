from PySide6.QtWidgets import (QMainWindow,QSpacerItem,QSizePolicy, QWidget,
                               QPushButton, QListWidget,QSplitter, QVBoxLayout,
                               QHBoxLayout, QStyleFactory)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from Rozwijane_menu import ScrollableMenu
from button import StyledButton


class Kreator(QMainWindow):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    LEFT_PANEL_WIDTH = 400

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Garage Door Designer")
        self.setGeometry(100, 100, self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

    def _create_left_panel(self):
        left_widget = QWidget()
        left_widget.setFixedWidth(self.LEFT_PANEL_WIDTH)
        left_layout = QVBoxLayout(left_widget)

        navigation_menu = ScrollableMenu()
        left_layout.addWidget(navigation_menu)

        return left_widget

    def _create_right_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        openGLWidget = QOpenGLWidget()
        openGLWidget.setObjectName("openGLWidget")
        right_layout.addWidget(openGLWidget)

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        self.back_button = StyledButton("Cofnij")
        self.save_button = StyledButton("Zapisz")

        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.save_button)

        right_layout.addWidget(buttons_widget)

        return right_widget






