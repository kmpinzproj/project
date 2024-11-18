import sqlite3

class DatabaseManager:

    DB_PATH = '../resources/project_db.db'

    def connect(self):
        """Nawiązuje połączenie z bazą danych."""
        return sqlite3.connect(self.DB_PATH)

    def list_projects(self):
        """Wyświetla wszystkie rekordy z tabeli Projekt."""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Projekt")
            projects = cursor.fetchall()
            conn.close()
            return projects
        except sqlite3.Error as e:
            print(f"Błąd podczas listowania danych: {e}")
            return []

    def add_project(self, nazwa, typ_bramy, gate_data=None):
        """
        Dodaje nowy rekord do tabeli Projekt oraz odpowiadającą bramę.
        :param nazwa: Nazwa projektu.
        :param typ_bramy: Typ bramy projektu.
        :param gate_data: Słownik z danymi bramy, które będą wstawiane do odpowiedniej tabeli.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Dodaj nowy projekt
            cursor.execute(
                "INSERT INTO Projekt (nazwa, data_zapisu, typ_bramy) VALUES (?, CURRENT_TIMESTAMP, ?)",
                (nazwa, typ_bramy)
            )
            projekt_id = cursor.lastrowid  # Pobierz ID dodanego projektu

            # Dodaj bramę powiązaną z projektem
            # TODO do zrobienia po ustawieniu przycisków zapisu self.add_gate(cursor, projekt_id, typ_bramy, gate_data)

            conn.commit()
            conn.close()
            print("Dodano nowy projekt oraz powiązaną bramę.")
        except sqlite3.Error as e:
            print(f"Błąd podczas dodawania projektu i bramy: {e}")

    def add_gate(self, cursor, projekt_id, typ_bramy, gate_data):
        """
        Dodaje rekord do odpowiedniej tabeli bramy powiązanej z projektem.
        :param cursor: Obiekt kursora do bazy danych.
        :param projekt_id: ID projektu, do którego powiązana jest brama.
        :param typ_bramy: Typ bramy (np. segmentowa, roletowa).
        :param gate_data: Słownik z danymi specyficznymi dla typu bramy.
        """
        try:
            if typ_bramy == "segmentowa":
                cursor.execute("""
                    INSERT INTO BramaSegmentowa 
                    (projekt_id, rodzaj_przetloczenia, struktura_powierzchni, kolor_standardowy, kolor_ral, sposob_otwierania_drzwi, opcje_dodatkowe)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    projekt_id,
                    gate_data.get("rodzaj_przetloczenia"),
                    gate_data.get("struktura_powierzchni"),
                    gate_data.get("kolor_standardowy"),
                    gate_data.get("kolor_ral"),
                    gate_data.get("sposob_otwierania_drzwi"),
                    gate_data.get("opcje_dodatkowe")
                ))

            elif typ_bramy == "roletowa":
                cursor.execute("""
                    INSERT INTO BramaRoletowa 
                    (projekt_id, wysokosc_profili, kolor_standardowy, kolor_ral, sposob_otwierania_bramy, przeszklenia)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    projekt_id,
                    gate_data.get("wysokosc_profili"),
                    gate_data.get("kolor_standardowy"),
                    gate_data.get("kolor_ral"),
                    gate_data.get("sposob_otwierania_bramy"),
                    gate_data.get("przeszklenia")
                ))

            elif typ_bramy == "rozwierana":
                cursor.execute("""
                    INSERT INTO BramaRozwierana 
                    (projekt_id, ilosc_skrzydel, ocieplenie, uklad_wypelnienia, kolor_standardowy, kolor_ral, przeszklenia, opcje_dodatkowe)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    projekt_id,
                    gate_data.get("ilosc_skrzydel"),
                    gate_data.get("ocieplenie"),
                    gate_data.get("uklad_wypelnienia"),
                    gate_data.get("kolor_standardowy"),
                    gate_data.get("kolor_ral"),
                    gate_data.get("przeszklenia"),
                    gate_data.get("opcje_dodatkowe")
                ))

            elif typ_bramy == "uchylna":
                cursor.execute("""
                    INSERT INTO BramaUchylna 
                    (projekt_id, uklad_wypelnienia, kolor_standardowy, kolor_ral, sposob_otwierania_drzwi, przeszklenia, drzwi_przejsciowe, opcje_dodatkowe)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    projekt_id,
                    gate_data.get("uklad_wypelnienia"),
                    gate_data.get("kolor_standardowy"),
                    gate_data.get("kolor_ral"),
                    gate_data.get("sposob_otwierania_drzwi"),
                    gate_data.get("przeszklenia"),
                    gate_data.get("drzwi_przejsciowe"),
                    gate_data.get("opcje_dodatkowe")
                ))
            else:
                raise ValueError(f"Nieznany typ bramy: {typ_bramy}")

        except sqlite3.Error as e:
            print(f"Błąd podczas dodawania bramy: {e}")

    def get_project(self, projekt_id):
        """
        Pobiera szczegóły projektu oraz informacje o powiązanej bramie w zależności od jej typu.

        Zwraca: Słownik zawierający dane projektu oraz powiązanej bramy lub None, jeśli projekt nie istnieje
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Pobierz szczegóły projektu
            cursor.execute("SELECT * FROM Projekt WHERE id = ?", (projekt_id,))
            project = cursor.fetchone()

            if not project:
                conn.close()
                print("Projekt o podanym ID nie istnieje.")
                return None

            # Słownik na dane wyjściowe
            project_data = {
                "projekt": {
                    "id": project[0],
                    "nazwa": project[1],
                    "data_zapisu": project[2],
                    "typ_bramy": project[3]
                },
                "brama": None  # Brama zostanie uzupełniona poniżej
            }

            # Pobierz dane o bramie na podstawie typu bramy
            typ_bramy = project[3]

            if typ_bramy == "segmentowa":
                cursor.execute("SELECT * FROM BramaSegmentowa WHERE projekt_id = ?", (projekt_id,))
                brama = cursor.fetchone()
                if brama:
                    project_data["brama"] = {
                        "rodzaj_przetloczenia": brama[2],
                        "struktura_powierzchni": brama[3],
                        "kolor_standardowy": brama[4],
                        "kolor_ral": brama[5],
                        "sposob_otwierania_drzwi": brama[6],
                        "opcje_dodatkowe": brama[7]
                    }

            elif typ_bramy == "roletowa":
                cursor.execute("SELECT * FROM BramaRoletowa WHERE projekt_id = ?", (projekt_id,))
                brama = cursor.fetchone()
                if brama:
                    project_data["brama"] = {
                        "wysokosc_profili": brama[2],
                        "kolor_standardowy": brama[3],
                        "kolor_ral": brama[4],
                        "sposob_otwierania_bramy": brama[5],
                        "przeszklenia": brama[6]
                    }

            elif typ_bramy == "rozwierana":
                cursor.execute("SELECT * FROM BramaRozwierana WHERE projekt_id = ?", (projekt_id,))
                brama = cursor.fetchone()
                if brama:
                    project_data["brama"] = {
                        "ilosc_skrzydel": brama[2],
                        "ocieplenie": brama[3],
                        "uklad_wypelnienia": brama[4],
                        "kolor_standardowy": brama[5],
                        "kolor_ral": brama[6],
                        "przeszklenia": brama[7],
                        "opcje_dodatkowe": brama[8]
                    }

            elif typ_bramy == "uchylna":
                cursor.execute("SELECT * FROM BramaUchylna WHERE projekt_id = ?", (projekt_id,))
                brama = cursor.fetchone()
                if brama:
                    project_data["brama"] = {
                        "uklad_wypelnienia": brama[2],
                        "kolor_standardowy": brama[3],
                        "kolor_ral": brama[4],
                        "sposob_otwierania_drzwi": brama[5],
                        "przeszklenia": brama[6],
                        "drzwi_przejsciowe": brama[7],
                        "opcje_dodatkowe": brama[8]
                    }

            conn.close()
            return project_data

        except sqlite3.Error as e:
            print(f"Błąd podczas pobierania danych projektu: {e}")
            return None


# TESTOWANIE BAZY DANYCH
if __name__ == "__main__":
    db_manager = DatabaseManager()

    # Dodanie nowego projektu
    db_manager.add_project("Projekt G", "Brama Segmentowa")
    db_manager.add_project("Projekt H", "Brama Roletowa")
    db_manager.add_project("Projekt I", "Brama Uchylna")
    db_manager.add_project("Projekt J", "Brama Rozwierana")
    db_manager.add_project("Projekt K", "Brama Uchylna")

    # Listowanie projektów
    projekty = db_manager.list_projects()
    for projekt in projekty:
        print(projekt)
