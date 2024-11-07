from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class CustomListWidgetItem(QWidget):
    def __init__(self, file_name, icon_path, parent=None):
        super().__init__(parent)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Ikona
        icon_label = QLabel(self)
        icon_label.setPixmap(QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignCenter)

        # Nazwa pliku
        file_label = QLabel(file_name, self)
        file_label.setAlignment(Qt.AlignCenter)

        # Dodanie ikony i etykiety do układu
        layout.addWidget(icon_label)
        layout.addWidget(file_label)

        # Styl podstawowy (bez ramki)
        self.setStyleSheet("border: 2px solid transparent;")

    def set_selected(self, selected):
        """Zmień styl ramki w zależności od stanu zaznaczenia."""
        if selected:
            self.setStyleSheet("border: 2px solid red;")
        else:
            self.setStyleSheet("border: 2px solid transparent;")