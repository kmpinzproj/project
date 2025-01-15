from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class CustomListWidgetItem(QWidget):
    """
    Klasa reprezentująca niestandardowy element listy w widżecie.

    Element zawiera ikonę oraz nazwę pliku, które są wyświetlane w jednym QLabel.
    Umożliwia dynamiczną zmianę tła w zależności od stanu zaznaczenia.
    """
    def __init__(self, file_name, icon_path, parent=None):
        """
        Inicjalizuje element listy z podaną ikoną i nazwą pliku.

        Args:
            file_name (str): Nazwa pliku do wyświetlenia.
            icon_path (str): Ścieżka do pliku ikony.
            parent (QWidget, optional): Rodzic widżetu. Domyślnie None.
        """
        super().__init__(parent)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)  # Ustawienie marginesów na zero

        # Łączenie ikony i nazwy pliku w jednym QLabel
        combined_label = QLabel(self)
        icon_pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        combined_label.setPixmap(icon_pixmap)
        combined_label.setText(f"<p align='center'><img src='{icon_path}' width='64' height='64'><br>{file_name}</p>")
        combined_label.setAlignment(Qt.AlignCenter)
        combined_label.setStyleSheet("background-color: transparent;")  # Przezroczyste tło na start

        # Dodanie QLabel do układu
        layout.addWidget(combined_label)

        # Przechowuj etykietę jako atrybut instancji, aby zmieniać jej tło w zależności od zaznaczenia
        self.combined_label = combined_label

    def set_selected(self, selected):
        """
        Zmienia kolor tła w zależności od stanu zaznaczenia.

        Args:
            selected (bool): True, jeśli element jest zaznaczony, False w przeciwnym przypadku.
        """
        if selected:
            self.combined_label.setStyleSheet("background-color: lightgreen;")  # Zielone tło
        else:
            self.combined_label.setStyleSheet("background-color: transparent;")  # Przezroczyste tło