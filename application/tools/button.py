from PySide6.QtWidgets import QPushButton

class StyledButton(QPushButton):
    """
    Klasa reprezentująca niestandardowy przycisk z własnym stylem.

    Przyciski posiadają zaokrąglone rogi, różne kolory dla stanów (normalny,
    najechany, wciśnięty, wyłączony) oraz dopasowane odstępy i czcionkę.
    """
    def __init__(self, text, parent=None):
        """
        Inicjalizuje przycisk z podanym tekstem oraz stosuje stylizację CSS.

        Args:
            text (str): Tekst wyświetlany na przycisku.
            parent (QWidget, optional): Rodzic przycisku. Domyślnie None.
        """
        super().__init__(text, parent)

        self.setStyleSheet("""
            QPushButton {
                background-color: #6e6e6e;  /* Gray background similar to the button in the screenshot */
                color: white;
                border: none;              /* Remove border */
                border-radius: 8px;        /* Rounded corners */
                padding: 10px;             /* Padding for spacing */
                font-size: 14px;           /* Font size */
            }
            QPushButton:hover {
                background-color: #5c5c5c;  /* Slightly darker gray when hovered */
            }
            QPushButton:pressed {
                background-color: #4a4a4a;  /* Even darker gray when pressed */
            }
            QPushButton:disabled {
                background-color: #bdc3c7;  /* Gray for disabled state */
                color: #7f8c8d;             /* Lighter gray text */
            }
        """)