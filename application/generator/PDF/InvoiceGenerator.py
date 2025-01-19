import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from application.DatabaseManager import DatabaseManager

# Rejestracja czcionki DejaVuSans z poprawioną ścieżką
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
        print(f"Błąd podczas wczytywania pliku JSON: {e}")
        return {}


def calculate_price(data, db_manager):
    """
    Oblicza cenę na podstawie danych o produkcie i bazy danych.

    Args:
        data (dict): Dane o produkcie.
        db_manager (DatabaseManager): Instancja klasy DatabaseManager do pobierania cen.

    Returns:
        tuple: Całkowita cena i szczegóły cenowe jako lista.
    """
    gate_type = data.get("Typ bramy")

    try:
        width = int(data.get("Wymiary", {}).get("Szerokość", 2500))
    except (ValueError, TypeError):
        width = 2500

    try:
        height = int(data.get("Wymiary", {}).get("Wysokość", 2125))
    except (ValueError, TypeError):
        height = 2125

    price = db_manager.get_price(gate_type, 'Bazowa', 'Cena')
    price_details = []

    price_details.append(f"Cena bazowa: {gate_type} (+{price} zł)")

    for param, option in data.items():
        if param in ["Typ bramy", "Wymiary", "Nazwa projektu", "Kolor standardowy", "Kolor RAL"]:
            continue

        if isinstance(option, list):
            for single_option in option:
                if isinstance(single_option, (str, int, float)):
                    surcharge = db_manager.get_price(gate_type, param, str(single_option))
                    if surcharge > 0:
                        price += surcharge
                        price_details.append(f"{param}: {single_option} (+{surcharge} zł)")
        elif isinstance(option, (str, int, float)):
            surcharge = db_manager.get_price(gate_type, param, str(option))
            if surcharge > 0:
                price += surcharge
                price_details.append(f"{param}: {option} (+{surcharge} zł)")

    extra_width = max(0, width - 2200)
    extra_height = max(0, height - 2000)

    extra_width_rate = 0.5  # Cena za każdy dodatkowy mm szerokości
    extra_height_rate = 0.5  # Cena za każdy dodatkowy mm wysokości

    extra_width_cost = extra_width * extra_width_rate
    extra_height_cost = extra_height * extra_height_rate

    if extra_width > 0:
        price += extra_width_cost
        price_details.append(f"Nadmiarowa szerokość: +{extra_width} mm (+{extra_width_cost} zł)")

    if extra_height > 0:
        price += extra_height_cost
        price_details.append(f"Nadmiarowa wysokość: +{extra_height} mm (+{extra_height_cost} zł)")

    return price, price_details


class InvoiceGenerator:
    """
    Klasa do generowania faktur w formacie PDF.
    """
    def __init__(self, output_path="invoice.pdf"):
        """
        Inicjalizuje generator faktur.

        Args:
            output_path (str): Ścieżka do zapisu wygenerowanej faktury.
        """
        self.output_path = output_path
        self.db_manager = DatabaseManager()

    def generate_invoice(self):
        """
        Generuje fakturę VAT w formacie PDF na podstawie danych o produkcie i nabywcy.
        """
        product_parameters = load_json_data("../resources/selected_options.json")
        customer_data = load_json_data("../resources/invoice_data.json")  # Wczytanie danych nabywcy
        total_price, price_details = calculate_price(product_parameters, self.db_manager)

        pdf = SimpleDocTemplate(self.output_path, pagesize=A4, leftMargin=20, rightMargin=20, topMargin=20,
                                bottomMargin=20)
        elements = []

        styles = getSampleStyleSheet()
        title_style = styles['Title']
        normal_style = styles['Normal']
        bold_style = styles['Heading2']

        title_style.fontName = 'DejaVuSans'
        normal_style.fontName = 'DejaVuSans'
        bold_style.fontName = 'DejaVuSans'

        elements.append(Paragraph('FAKTURA VAT', title_style))
        elements.append(Paragraph('Numer faktury: FV/2024/0001', normal_style))  # Dodanie numeru faktury
        elements.append(Spacer(1, 10))

        elements.append(Paragraph('<b>Sprzedawca:</b>', bold_style))
        elements.append(Paragraph('Firma XYZ Sp. z o.o.', normal_style))
        elements.append(Spacer(1, 8))

        elements.append(Paragraph('<b>Nabywca:</b>', bold_style))

        # Dodanie danych nabywcy (klucz: wartość)
        for key, value in customer_data.items():
            elements.append(Paragraph(f"{key}: {value}", normal_style))

        elements.append(Spacer(1, 10))

        table_data = [['LP', 'Parametr', 'Szczegóły', 'Cena netto (zł)', 'Ilość', 'Cena Brutto (zł)']]
        total_netto = 0
        total_brutto = 0
        VAT_RATE = 23  # VAT w Polsce (23%)

        row_index = 1
        for detail in price_details:
            param_name, param_value = detail.split(": ", 1)
            price_text = param_value.split(" (+")[0]
            surcharge = float(param_value.split("(+")[1].split(" zł")[0])

            quantity = 1
            total_netto_value = surcharge * quantity
            vat_value = total_netto_value * (VAT_RATE / 100)
            total_brutto_value = total_netto_value + vat_value

            total_netto += total_netto_value
            total_brutto += total_brutto_value

            row = [
                str(row_index),
                param_name,
                price_text,
                f"{surcharge:.2f}",
                str(quantity),
                f"{total_brutto_value:.2f}"
            ]
            table_data.append(row)
            row_index += 1

        total_width = A4[0] - 40
        col_widths = [0.05 * total_width, 0.25 * total_width, 0.25 * total_width, 0.15 * total_width,
                      0.10 * total_width, 0.20 * total_width]

        table = Table(table_data, colWidths=col_widths)
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(table_style)

        elements.append(table)
        elements.append(Spacer(1, 10))

        summary_data = [
            ['RAZEM NETTO', f"{total_netto:.2f} zł"],
            ['RAZEM BRUTTO', f"{total_brutto:.2f} zł"]
        ]

        summary_table = Table(summary_data, colWidths=[0.7 * total_width, 0.3 * total_width])
        summary_table_style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        summary_table.setStyle(summary_table_style)

        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        elements.append(Paragraph('Dziękujemy za zakupy!', bold_style))

        pdf.build(elements)
        print(f"Faktura została zapisana jako {self.output_path}")


if __name__ == "__main__":
    invoice_generator = InvoiceGenerator(output_path="faktura.pdf")
    invoice_generator.generate_invoice()
