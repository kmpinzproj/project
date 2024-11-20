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
        :param typ_bramy: Typ bramy projektu (np. "segmentowa", "roletowa").
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

            # Dodaj rekord do odpowiedniej tabeli bramy
            if gate_data:
                self.add_gate(cursor, projekt_id, typ_bramy, gate_data)

            conn.commit()
            conn.close()
            print(f"Projekt '{nazwa}' z typem bramy '{typ_bramy}' został dodany wraz z danymi bramy.")
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

    def add_project_from_json(self, project_json):
        """
        Dodaje projekt i powiązaną bramę na podstawie danych z JSON.

        :param project_json: Słownik reprezentujący dane projektu i bramy.
        :return: None
        """
        try:
            # Pobranie klucza głównego (typu bramy) i danych
            if len(project_json) != 1:
                raise ValueError("JSON powinien zawierać dokładnie jeden typ bramy jako klucz główny.")

            gate_type, gate_data = list(project_json.items())[0]  # Klucz: typ bramy, Wartość: dane bramy

            # Dopasowanie typu bramy do bazy danych
            typ_bramy_map = {
                "Brama Segmentowa": "segmentowa",
                "Brama Roletowa": "roletowa",
                "Brama Rozwierana": "rozwierana",
                "Brama Uchylna": "uchylna",
            }

            if gate_type not in typ_bramy_map:
                raise ValueError(f"Nieznany typ bramy: {gate_type}")

            typ_bramy = typ_bramy_map[gate_type]

            # Tworzenie projektu na podstawie danych
            project_name = f"Projekt {gate_type}"  # Nazwa generowana na podstawie typu bramy
            self.add_project(
                nazwa=project_name,
                typ_bramy=typ_bramy,
                gate_data=self._map_gate_data(typ_bramy, gate_data)
            )
            print(f"Projekt '{project_name}' z typem bramy '{typ_bramy}' został dodany.")
        except Exception as e:
            print(f"Błąd podczas dodawania projektu z JSON: {e}")

    def _map_gate_data(self, typ_bramy, gate_data):
        """
        Mapuje dane bramy z JSON na format wymagany przez bazę danych.

        :param typ_bramy: Typ bramy (np. "segmentowa", "roletowa", itp.)
        :param gate_data: Słownik danych bramy.
        :return: Słownik dopasowany do struktury bazy danych.
        """
        # Mapowanie danych na podstawie typu bramy
        try:
            if typ_bramy == "segmentowa":
                return {
                    "rodzaj_przetloczenia": gate_data.get("Rodzaj przetłoczenia", None),
                    "struktura_powierzchni": gate_data.get("Struktura powierzchni", None),
                    "kolor_standardowy": gate_data.get("Kolor standardowy", None),
                    "kolor_ral": gate_data.get("Kolor", None),
                    "sposob_otwierania_drzwi": gate_data.get("Sposób otwierania drzwi", None),
                    "opcje_dodatkowe": ", ".join(gate_data.get("Opcje dodatkowe", [])),
                }

            elif typ_bramy == "roletowa":
                return {
                    "wysokosc_profili": gate_data.get("Wysokość profili", None),
                    "kolor_standardowy": gate_data.get("Kolor standardowy", None),
                    "kolor_ral": gate_data.get("Kolor", None),
                    "sposob_otwierania_bramy": gate_data.get("Sposób otwierania bramy", None),
                    "przeszklenia": gate_data.get("Przeszklenia", None),
                }

            elif typ_bramy == "rozwierana":
                return {
                    "ilosc_skrzydel": gate_data.get("Ilość skrzydeł", None),
                    "ocieplenie": gate_data.get("Ocieplenie", None),
                    "uklad_wypelnienia": gate_data.get("Układ wypełnienia", None),
                    "kolor_standardowy": gate_data.get("Kolor standardowy", None),
                    "kolor_ral": gate_data.get("Kolor", None),
                    "przeszklenia": gate_data.get("Przeszklenia", None),
                    "opcje_dodatkowe": ", ".join(gate_data.get("Opcje dodatkowe", [])),
                }

            elif typ_bramy == "uchylna":
                return {
                    "uklad_wypelnienia": gate_data.get("Układ wypełnienia", None),
                    "kolor_standardowy": gate_data.get("Kolor standardowy", None),
                    "kolor_ral": gate_data.get("Kolor", None),
                    "sposob_otwierania_drzwi": gate_data.get("Sposób otwierania drzwi", None),
                    "przeszklenia": gate_data.get("Przeszklenia", None),
                    "drzwi_przejsciowe": gate_data.get("Drzwi przejściowe", None),
                    "opcje_dodatkowe": ", ".join(gate_data.get("Opcje dodatkowe", [])),
                }

            else:
                raise ValueError(f"Nieobsługiwany typ bramy: {typ_bramy}")

        except Exception as e:
            print(f"Błąd podczas mapowania danych dla typu '{typ_bramy}': {e}")
            return {}

    def get_project_by_name(self, project_name):
        """
        Pobiera szczegóły projektu oraz powiązaną bramę na podstawie nazwy projektu.

        :param project_name: Nazwa projektu.
        :return: Słownik zawierający dane projektu oraz powiązanej bramy.
        """
        conn = self.connect()
        cursor = conn.cursor()

        # Pobierz szczegóły projektu na podstawie nazwy
        cursor.execute("SELECT * FROM Projekt WHERE nazwa = ?", (project_name,))
        project = cursor.fetchone()

        if not project:
            conn.close()
            raise ValueError(f"Projekt o nazwie '{project_name}' nie istnieje.")

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
            cursor.execute("SELECT * FROM BramaSegmentowa WHERE projekt_id = ?", (project[0],))
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
            cursor.execute("SELECT * FROM BramaRoletowa WHERE projekt_id = ?", (project[0],))
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
            cursor.execute("SELECT * FROM BramaRozwierana WHERE projekt_id = ?", (project[0],))
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
            cursor.execute("SELECT * FROM BramaUchylna WHERE projekt_id = ?", (project[0],))
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


# TESTOWANIE BAZY DANYCH
if __name__ == "__main__":
    db_manager = DatabaseManager()
    #
    # # Dodanie nowego projektu
    # db_manager.add_project("Projekt G", "Brama Segmentowa")
    # db_manager.add_project("Projekt H", "Brama Roletowa")
    # db_manager.add_project("Projekt I", "Brama Uchylna")
    # db_manager.add_project("Projekt J", "Brama Rozwierana")
    # db_manager.add_project("Projekt K", "Brama Uchylna")

    # Listowanie projektów
    projekty = db_manager.list_projects()
    for projekt in projekty:
        print(projekt)

    # Załadowanie JSON jako słownika Python
    import json

    with open("selected_options.json", "r", encoding="utf-8") as file:
        project_json = json.load(file)

    # Dodanie projektu do bazy danych
    db_manager = DatabaseManager()
    db_manager.add_project_from_json(project_json)
