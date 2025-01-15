import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PySide6.QtWidgets import QFileDialog, QApplication
import os

# Rejestracja czcionki
pdfmetrics.registerFont(TTFont('DejaVuSans', '../resources/DejaVuSans.ttf'))

def load_json_data(file_path):
    """
    Wczytuje dane z pliku JSON.

    Args:
        file_path (str): Ścieżka do pliku JSON.

    Returns:
        dict: Dane załadowane z pliku JSON lub pusty słownik w przypadku błędu.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return {}

class PDFGenerator:
    """
    Klasa odpowiedzialna za generowanie pliku PDF z podsumowaniem projektu i szkicami.
    """
    def __init__(self, output_path="output.pdf"):
        """
        Inicjalizuje generator plików PDF.

        Args:
            output_path (str): Ścieżka do zapisu wygenerowanego pliku PDF.
        """
        self.output_path = output_path

    def create_pdf(self):
        """
        Generuje plik PDF na podstawie danych projektu i dodaje szkice jako obrazy.

        Dane projektu wczytywane są z pliku `../resources/selected_options.json`,
        a obrazy są ładowane z predefiniowanych ścieżek.

        Raises:
            Exception: Jeśli wystąpi błąd podczas generowania PDF.
        """
        product_data = load_json_data("../resources/selected_options.json")

        # Inicjalizacja dokumentu PDF
        pdf = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            leftMargin=20,
            rightMargin=20,
            topMargin=20,
            bottomMargin=20
        )
        elements = []

        # Style
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['Normal']
        title_style.fontName = 'DejaVuSans'
        normal_style.fontName = 'DejaVuSans'

        # Nagłówek
        elements.append(Paragraph("DOKUMENT PRODUKTU", title_style))
        elements.append(Spacer(1, 10))

        # Dane w tabeli
        table_data = []
        if product_data:
            for key, value in product_data.items():
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                table_data.append([Paragraph(str(key), normal_style), Paragraph(str(value), normal_style)])
        else:
            table_data.append(["Brak danych", ""])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Dodanie obrazów
        image_paths = [
            "../generator/image_with_arrows.png",
            "../generator/sketch_iso_no_diagonals.png"
        ]
        for image_path in image_paths:
            if os.path.exists(image_path):
                elements.append(Image(image_path, width=400, height=200))
            else:
                print(f"Image not found: {image_path}")

        pdf.build(elements)
        print(f"PDF saved at: {self.output_path}")